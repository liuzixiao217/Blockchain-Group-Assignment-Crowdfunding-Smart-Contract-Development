from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from web3 import Web3
import asyncio
import json
import sqlite3
from datetime import datetime
import os
from typing import List, Optional
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data Models
class CampaignStatus(BaseModel):
    goal: float
    raised: float
    progress: float
    deadline: str
    status: str
    backer_count: int
    goal_reached: bool
    funds_withdrawn: bool
    creator: str
    contract_balance: float

class Transaction(BaseModel):
    hash: str
    from_address: str
    value: float
    timestamp: str
    type: str

class Notification(BaseModel):
    id: str
    title: str
    message: str
    timestamp: str
    read: bool

class GasEstimate(BaseModel):
    gas_price_gwei: float
    gas_limit: int
    estimated_cost_eth: float
    estimated_cost_usd: float

class HealthStatus(BaseModel):
    status: str
    blockchain_connected: bool
    database: str
    timestamp: str
    backend_version: str

# Blockchain Service
class BlockchainService:
    def __init__(self):
        self.setup_blockchain()
        self.init_database()
        self.event_listening_task = None
        
    def setup_blockchain(self):
        """Setup blockchain connection"""
        try:
            self.rpc_url = os.getenv("RPC_URL", "https://eth-sepolia.g.alchemy.com/v2/isuYPjX2wCoJHttJBce3w")
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            
            if not self.w3.is_connected():
                raise Exception("Cannot connect to blockchain network")
            
            logger.info("✅ Blockchain connected successfully")
            
            # Load contract
            contract_address = os.getenv("CONTRACT_ADDRESS", "0x25D1Cb8E516750F8265329e86cD51d35D6C9C9D4")
            
            # Load ABI from file
            try:
                with open('../shared/contract_abi.json', 'r') as f:
                    contract_abi = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load ABI from file: {e}")
                # Fallback to a basic ABI if file not found
                contract_abi = [
                    {
                        "inputs": [],
                        "name": "goal",
                        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                        "stateMutability": "view",
                        "type": "function"
                    },
                    {
                        "inputs": [],
                        "name": "amountRaised",
                        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                        "stateMutability": "view",
                        "type": "function"
                    },
                    {
                        "inputs": [],
                        "name": "deadline",
                        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                        "stateMutability": "view",
                        "type": "function"
                    },
                    {
                        "inputs": [],
                        "name": "goalReached",
                        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                        "stateMutability": "view",
                        "type": "function"
                    },
                    {
                        "inputs": [],
                        "name": "fundsWithdrawn",
                        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                        "stateMutability": "view",
                        "type": "function"
                    },
                    {
                        "inputs": [],
                        "name": "creator",
                        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                        "stateMutability": "view",
                        "type": "function"
                    },
                    {
                        "inputs": [],
                        "name": "getStatus",
                        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
                        "stateMutability": "view",
                        "type": "function"
                    },
                    {
                        "inputs": [],
                        "name": "getContractBalance",
                        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                        "stateMutability": "view",
                        "type": "function"
                    },
                    {
                        "inputs": [],
                        "name": "getContributorCount",
                        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                        "stateMutability": "view",
                        "type": "function"
                    },
                    # Event definitions for listening - UPDATED to match frontend ABI
                    {
                        "anonymous": False,
                        "inputs": [
                            {
                                "indexed": False,
                                "internalType": "address",
                                "name": "backer",
                                "type": "address"
                            },
                            {
                                "indexed": False,
                                "internalType": "uint256",
                                "name": "amount",
                                "type": "uint256"
                            }
                        ],
                        "name": "Funded",
                        "type": "event"
                    },
                    {
                        "anonymous": False,
                        "inputs": [
                            {
                                "indexed": False,
                                "internalType": "uint256",
                                "name": "total",
                                "type": "uint256"
                            }
                        ],
                        "name": "GoalAchieved",
                        "type": "event"
                    },
                    {
                        "anonymous": False,
                        "inputs": [
                            {
                                "indexed": False,
                                "internalType": "address",
                                "name": "backer",
                                "type": "address"
                            },
                            {
                                "indexed": False,
                                "internalType": "uint256",
                                "name": "amount",
                                "type": "uint256"
                            }
                        ],
                        "name": "RefundClaimed",
                        "type": "event"
                    },
                    {
                        "anonymous": False,
                        "inputs": [
                            {
                                "indexed": False,
                                "internalType": "address",
                                "name": "creator",
                                "type": "address"
                            },
                            {
                                "indexed": False,
                                "internalType": "uint256",
                                "name": "amount",
                                "type": "uint256"
                            }
                        ],
                        "name": "FundsWithdrawn",
                        "type": "event"
                    }
                ]
            
            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=contract_abi
            )
            logger.info("✅ Contract initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Blockchain setup failed: {e}")
            raise
    
    def init_database(self):
        """Initialize SQLite database"""
        try:
            self.conn = sqlite3.connect('campaign_data.db', check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            
            # Transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tx_hash TEXT UNIQUE,
                    from_address TEXT,
                    value_eth REAL,
                    transaction_type TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    block_number INTEGER
                )
            ''')
            
            # Notifications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    read BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Cache table for performance
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            logger.info("✅ Database initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
    
    def setup_event_listeners(self):
        """Setup blockchain event listeners"""
        try:
            logger.info("🔄 Setting up blockchain event listeners...")
            
            # Start listening for events in background
            self.event_listening_task = asyncio.create_task(self.listen_for_events())
            logger.info("✅ Event listeners started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup event listeners: {e}")
    
    async def listen_for_events(self):
        """Listen for blockchain events"""
        last_block = self.w3.eth.block_number
        
        while True:
            try:
                current_block = self.w3.eth.block_number
                
                if current_block > last_block:
                    logger.info(f"🔍 Scanning blocks {last_block + 1} to {current_block} for events")
                    
                    # Look for Funded events (previously called Contribution)
                    funded_events = self.contract.events.Funded.get_logs(
                        fromBlock=last_block + 1,
                        toBlock=current_block
                    )
                    
                    for event in funded_events:
                        await self.handle_funded_event(event)
                    
                    # Look for FundsWithdrawn events
                    withdrawal_events = self.contract.events.FundsWithdrawn.get_logs(
                        fromBlock=last_block + 1,
                        toBlock=current_block
                    )
                    
                    for event in withdrawal_events:
                        await self.handle_withdrawal_event(event)
                    
                    # Look for RefundClaimed events (previously called Refund)
                    refund_claimed_events = self.contract.events.RefundClaimed.get_logs(
                        fromBlock=last_block + 1,
                        toBlock=current_block
                    )
                    
                    for event in refund_claimed_events:
                        await self.handle_refund_claimed_event(event)
                    
                    last_block = current_block
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in event listener: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    async def handle_funded_event(self, event):
        """Handle Funded events (previously called Contribution)"""
        try:
            tx_hash = event['transactionHash'].hex()
            from_address = event['args']['backer']  # Parameter name is 'backer' in the contract
            amount = event['args']['amount']
            value_eth = float(self.w3.from_wei(amount, 'ether'))
            
            # Get transaction details
            tx = self.w3.eth.get_transaction(tx_hash)
            tx_timestamp = self.get_block_timestamp(event['blockNumber'])
            
            # Save to database
            self.save_transaction(tx_hash, from_address, value_eth, "contribution")
            
            # Add notification
            self.add_notification(
                "New Contribution",
                f"Received {value_eth:.4f} ETH from {from_address[:8]}..."
            )
            
            logger.info(f"✅ Captured contribution: {value_eth:.4f} ETH from {from_address[:8]}...")
            
        except Exception as e:
            logger.error(f"❌ Error handling funded event: {e}")
    
    async def handle_withdrawal_event(self, event):
        """Handle funds withdrawal events"""
        try:
            tx_hash = event['transactionHash'].hex()
            creator = event['args']['creator']
            amount = event['args']['amount']
            value_eth = float(self.w3.from_wei(amount, 'ether'))
            
            # Save to database
            self.save_transaction(tx_hash, creator, value_eth, "withdrawal")
            
            # Add notification
            self.add_notification(
                "Funds Withdrawn",
                f"Creator withdrew {value_eth:.4f} ETH"
            )
            
            logger.info(f"✅ Captured withdrawal: {value_eth:.4f} ETH by creator")
            
        except Exception as e:
            logger.error(f"❌ Error handling withdrawal event: {e}")
    
    async def handle_refund_claimed_event(self, event):
        """Handle RefundClaimed events (previously called Refund)"""
        try:
            tx_hash = event['transactionHash'].hex()
            backer = event['args']['backer']  # Parameter name is 'backer' in the contract
            amount = event['args']['amount']
            value_eth = float(self.w3.from_wei(amount, 'ether'))
            
            # Save to database
            self.save_transaction(tx_hash, backer, value_eth, "refund")
            
            # Add notification
            self.add_notification(
                "Refund Processed",
                f"Refunded {value_eth:.4f} ETH to {backer[:8]}..."
            )
            
            logger.info(f"✅ Captured refund: {value_eth:.4f} ETH to {backer[:8]}...")
            
        except Exception as e:
            logger.error(f"❌ Error handling refund claimed event: {e}")
    
    def get_block_timestamp(self, block_number):
        """Get timestamp from block number"""
        try:
            block = self.w3.eth.get_block(block_number)
            return datetime.fromtimestamp(block.timestamp).strftime("%Y-%m-%d %H:%M:%S")
        except:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_campaign_status(self) -> CampaignStatus:
        """Get current campaign status from blockchain"""
        try:
            # Fetch data from blockchain
            goal = self.contract.functions.goal().call()
            amount_raised = self.contract.functions.amountRaised().call()
            deadline = self.contract.functions.deadline().call()
            goal_reached = self.contract.functions.goalReached().call()
            funds_withdrawn = self.contract.functions.fundsWithdrawn().call()
            creator = self.contract.functions.creator().call()
            
            # Handle optional functions gracefully
            try:
                status = self.contract.functions.getStatus().call()
            except:
                status = "Active" if not goal_reached else "Completed"
                
            try:
                contract_balance = self.contract.functions.getContractBalance().call()
            except:
                contract_balance = amount_raised
                
            try:
                backer_count = self.contract.functions.getContributorCount().call()
            except:
                backer_count = 0
            
            # Convert units
            goal_eth = self.w3.from_wei(goal, 'ether')
            raised_eth = self.w3.from_wei(amount_raised, 'ether')
            balance_eth = self.w3.from_wei(contract_balance, 'ether')
            progress = (raised_eth / goal_eth) * 100 if goal_eth > 0 else 0
            
            return CampaignStatus(
                goal=float(goal_eth),
                raised=float(raised_eth),
                progress=float(progress),
                deadline=datetime.fromtimestamp(deadline).strftime("%Y-%m-%d %H:%M:%S"),
                status=status,
                backer_count=backer_count,
                goal_reached=goal_reached,
                funds_withdrawn=funds_withdrawn,
                creator=creator,
                contract_balance=float(balance_eth)
            )
            
        except Exception as e:
            logger.error(f"Failed to get campaign status: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch campaign status: {str(e)}")
    
    def save_transaction(self, tx_hash: str, from_address: str, value_eth: float, tx_type: str):
        """Save transaction to database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO transactions 
                (tx_hash, from_address, value_eth, transaction_type, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (tx_hash, from_address, value_eth, tx_type, datetime.now()))
            self.conn.commit()
            logger.info(f"✅ Transaction saved: {tx_hash}")
        except Exception as e:
            logger.error(f"Failed to save transaction: {e}")
    
    def get_transaction_history(self, limit: int = 50) -> List[Transaction]:
        """Get transaction history from database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT tx_hash, from_address, value_eth, transaction_type, timestamp
                FROM transactions 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            transactions = []
            for row in cursor.fetchall():
                transactions.append(Transaction(
                    hash=row['tx_hash'],
                    from_address=row['from_address'],
                    value=row['value_eth'],
                    type=row['transaction_type'],
                    timestamp=row['timestamp']
                ))
            
            return transactions
        except Exception as e:
            logger.error(f"Failed to get transaction history: {e}")
            return []
    
    def add_notification(self, title: str, message: str):
        """Add notification to database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO notifications (title, message)
                VALUES (?, ?)
            ''', (title, message))
            self.conn.commit()
            logger.info(f"✅ Notification added: {title}")
        except Exception as e:
            logger.error(f"Failed to add notification: {e}")
    
    def get_notifications(self, unread_only: bool = False) -> List[Notification]:
        """Get notifications from database"""
        try:
            cursor = self.conn.cursor()
            if unread_only:
                cursor.execute('''
                    SELECT id, title, message, timestamp, read 
                    FROM notifications 
                    WHERE read = FALSE 
                    ORDER BY timestamp DESC
                ''')
            else:
                cursor.execute('''
                    SELECT id, title, message, timestamp, read 
                    FROM notifications 
                    ORDER BY timestamp DESC
                ''')
            
            notifications = []
            for row in cursor.fetchall():
                notifications.append(Notification(
                    id=str(row['id']),
                    title=row['title'],
                    message=row['message'],
                    timestamp=row['timestamp'],
                    read=bool(row['read'])
                ))
            
            return notifications
        except Exception as e:
            logger.error(f"Failed to get notifications: {e}")
            return []
    
    def estimate_gas_cost(self, operation: str) -> GasEstimate:
        """Estimate gas cost for operations"""
        try:
            gas_price = self.w3.eth.gas_price
            gas_price_gwei = self.w3.from_wei(gas_price, 'gwei')
            
            # Estimated gas limits for different operations
            gas_limits = {
                'support': 50000,
                'withdraw': 30000,
                'refund': 35000,
                'update': 25000
            }
            
            gas_limit = gas_limits.get(operation, 50000)
            total_gas = gas_limit * gas_price
            total_eth = self.w3.from_wei(total_gas, 'ether')
            
            # Assume ETH price is $1800 (should be from API in production)
            eth_price = 1800
            
            return GasEstimate(
                gas_price_gwei=float(gas_price_gwei),
                gas_limit=gas_limit,
                estimated_cost_eth=float(total_eth),
                estimated_cost_usd=float(total_eth) * eth_price
            )
        except Exception as e:
            logger.error(f"Gas estimation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Gas estimation failed: {str(e)}")
    
    def get_health_status(self) -> HealthStatus:
        """Get system health status"""
        try:
            blockchain_connected = self.w3.is_connected()
            database_connected = self.conn is not None
            
            status = "healthy" if blockchain_connected and database_connected else "degraded"
            if not blockchain_connected:
                status = "unhealthy"
            
            return HealthStatus(
                status=status,
                blockchain_connected=blockchain_connected,
                database="connected" if database_connected else "disconnected",
                timestamp=datetime.now().isoformat(),
                backend_version="1.0.0"
            )
        except Exception as e:
            return HealthStatus(
                status="unhealthy",
                blockchain_connected=False,
                database="error",
                timestamp=datetime.now().isoformat(),
                backend_version="1.0.0"
            )

# Initialize FastAPI app
app = FastAPI(
    title="Crowdfunding Platform Backend API",
    description="Backend service for Blockchain Crowdfunding Platform - CDS528 Group Project",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global service instance
blockchain_service = BlockchainService()

# API Routes
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Crowdfunding Platform Backend API", 
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/campaign/status", response_model=CampaignStatus, tags=["Campaign"])
async def get_campaign_status():
    """Get current campaign status"""
    return blockchain_service.get_campaign_status()

@app.get("/api/transactions/history", response_model=List[Transaction], tags=["Transactions"])
async def get_transaction_history(limit: int = 50):
    """Get transaction history"""
    return blockchain_service.get_transaction_history(limit)

@app.get("/api/notifications", response_model=List[Notification], tags=["Notifications"])
async def get_notifications(unread_only: bool = False):
    """Get notifications"""
    return blockchain_service.get_notifications(unread_only)

@app.post("/api/notifications/read/{notification_id}", tags=["Notifications"])
async def mark_notification_read(notification_id: str):
    """Mark notification as read"""
    try:
        cursor = blockchain_service.conn.cursor()
        cursor.execute('UPDATE notifications SET read = TRUE WHERE id = ?', (notification_id,))
        blockchain_service.conn.commit()
        return {"status": "success", "message": "Notification marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/gas/estimate/{operation}", response_model=GasEstimate, tags=["Utilities"])
async def estimate_gas(operation: str):
    """Estimate gas cost for blockchain operations"""
    return blockchain_service.estimate_gas_cost(operation)

@app.get("/api/health", response_model=HealthStatus, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return blockchain_service.get_health_status()

# Test endpoint to add sample data
@app.post("/api/test/add-sample-data")
async def add_sample_data():
    """Add sample transaction and notification for testing"""
    blockchain_service.save_transaction(
        "0x5afd1c54fe44d1a3f80c0444b6782e34011fd4698c919469d86cd45a22456fbee",
        "0xf7E5127d51d26C773510F6DD91BD0BD66837962f",
        0.0001,
        "contribution"
    )
    
    blockchain_service.add_notification(
        "Test Contribution", 
        "Received 0.0001 ETH test transaction"
    )
    
    return {"status": "success", "message": "Sample data added successfully"}

# Background tasks
async def periodic_cache_update():
    """Periodically update cache and check for new events"""
    while True:
        try:
            # Update campaign status cache
            status = blockchain_service.get_campaign_status()
            
            await asyncio.sleep(30)  # Update every 30 seconds
            
        except Exception as e:
            logger.error(f"Cache update error: {e}")
            await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("🚀 Starting Crowdfunding Backend Service...")
    # Start event listeners
    blockchain_service.setup_event_listeners()
    asyncio.create_task(periodic_cache_update())

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("🛑 Shutting down Backend Service...")
    # Cancel event listening task
    if blockchain_service.event_listening_task:
        blockchain_service.event_listening_task.cancel()
    if hasattr(blockchain_service, 'conn'):
        blockchain_service.conn.close()

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    logger.info(f"🌐 Starting server on http://{host}:{port}")
    logger.info(f"📚 API Documentation: http://{host}:{port}/docs")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )