import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from web3 import Web3
import json
import threading
import time
from datetime import datetime
import os
import requests  # NEW: For backend API calls

class CrowdfundingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Blockchain Crowdfunding Platform - CDS528 Group Project")
        self.root.geometry("900x700")
        
        # Backend API configuration - NEW
        self.backend_url = "http://127.0.0.1:8000/api"  # Use 127.0.0.1 to bypass proxy
        self.use_backend = True  # Whether to use backend
        self.backend_available = False  # Backend availability status
        
        # Use your Alchemy RPC URL
        self.rpc_endpoints = [
            'https://eth-sepolia.g.alchemy.com/v2/isuYPjX2wCoJHttJBce3w',  # Your Alchemy URL
            'https://sepolia.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161',
            'https://rpc.sepolia.org'
        ]
        
        # Your wallet private key (from env file)
        self.default_private_key = "3763b642be22ad4d0c6ef29a39680c6077aecbc1abc8cc608028ad5f928dc8c8"
        
        self.current_rpc_index = 0
        self.w3 = None
        self.contract = None
        self.account = None
        
        # Contract configuration
        self.contract_address = "0x25D1Cb8E516750F8265329e86cD51d35D6C9C9D4"
        self.contract_abi = [
            {
                "inputs": [
                    {"internalType": "uint256", "name": "_goal", "type": "uint256"},
                    {"internalType": "uint256", "name": "_duration", "type": "uint256"}
                ],
                "stateMutability": "nonpayable",
                "type": "constructor"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": False, "internalType": "address", "name": "backer", "type": "address"},
                    {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}
                ],
                "name": "Funded",
                "type": "event"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": False, "internalType": "uint256", "name": "total", "type": "uint256"}
                ],
                "name": "GoalAchieved",
                "type": "event"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": False, "internalType": "address", "name": "backer", "type": "address"},
                    {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}
                ],
                "name": "RefundClaimed",
                "type": "event"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": False, "internalType": "address", "name": "creator", "type": "address"},
                    {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}
                ],
                "name": "FundsWithdrawn",
                "type": "event"
            },
            {
                "inputs": [],
                "name": "amountRaised",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "startIndex", "type": "uint256"},
                    {"internalType": "uint256", "name": "endIndex", "type": "uint256"}
                ],
                "name": "batchRefund",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "claimRefund",
                "outputs": [],
                "stateMutability": "nonpayable",
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
                "name": "deadline",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "forceUpdate",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "fund",
                "outputs": [],
                "stateMutability": "payable",
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
            {
                "inputs": [],
                "name": "getStatus",
                "outputs": [{"internalType": "string", "name": "", "type": "string"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "goal",
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
                "inputs": [
                    {"internalType": "address", "name": "", "type": "address"}
                ],
                "name": "contributions",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "", "type": "uint256"}
                ],
                "name": "contributors",
                "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "withdrawFunds",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "stateMutability": "payable",
                "type": "receive"
            }
        ]
        
        self.setup_ui()
        self.check_backend_connection()  # NEW: Check backend connection
        self.connect_to_blockchain()
    
    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Blockchain Crowdfunding Platform - Sepolia Testnet", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Backend Status Frame - NEW
        backend_frame = ttk.LabelFrame(main_frame, text="Backend Service Status", padding="5")
        backend_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.backend_status_label = ttk.Label(backend_frame, text="Checking backend connection...")
        self.backend_status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.backend_toggle_btn = ttk.Button(backend_frame, text="Switch to Blockchain", command=self.toggle_backend)
        self.backend_toggle_btn.grid(row=0, column=1, padx=(10, 0))
        
        # Network status
        network_frame = ttk.LabelFrame(main_frame, text="Network Status", padding="5")
        network_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.network_label = ttk.Label(network_frame, text="Connecting...")
        self.network_label.grid(row=0, column=0, sticky=tk.W)
        
        self.rpc_label = ttk.Label(network_frame, text="")
        self.rpc_label.grid(row=0, column=1, padx=(20, 0))
        
        # Wallet connection status
        self.status_frame = ttk.LabelFrame(main_frame, text="Wallet Status", padding="5")
        self.status_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(self.status_frame, text="Using default wallet")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.connect_btn = ttk.Button(self.status_frame, text="Connect Default Wallet", command=self.connect_default_wallet)
        self.connect_btn.grid(row=0, column=1, padx=(10, 0))
        
        self.custom_connect_btn = ttk.Button(self.status_frame, text="Use Other Wallet", command=self.connect_custom_wallet)
        self.custom_connect_btn.grid(row=0, column=2, padx=(10, 0))
        
        self.refresh_btn = ttk.Button(self.status_frame, text="Refresh Data", command=self.refresh_data)
        self.refresh_btn.grid(row=0, column=3, padx=(10, 0))
        
        # Campaign information frame
        info_frame = ttk.LabelFrame(main_frame, text="Crowdfunding Contract Information", padding="5")
        info_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Contract address
        ttk.Label(info_frame, text="Contract Address:").grid(row=0, column=0, sticky=tk.W, pady=2)
        contract_addr_label = ttk.Label(info_frame, text=self.contract_address, foreground="blue")
        contract_addr_label.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Campaign details
        details = [
            ("Funding Goal:", "goal_label"),
            ("Amount Raised:", "raised_label"), 
            ("Progress:", "progress_label"),
            ("Deadline:", "deadline_label"),
            ("Status:", "status_label"),
            ("Creator:", "creator_label"),
            ("Contract Balance:", "balance_label"),
            ("Goal Reached:", "goal_reached_label"),
            ("Funds Withdrawn:", "withdrawn_label")
        ]
        
        for i, (label_text, var_name) in enumerate(details):
            ttk.Label(info_frame, text=label_text).grid(row=i+1, column=0, sticky=tk.W, pady=2)
            setattr(self, var_name, ttk.Label(info_frame, text="Loading..."))
            getattr(self, var_name).grid(row=i+1, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(info_frame, orient='horizontal', length=400, mode='determinate')
        self.progress_bar.grid(row=len(details)+1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Action buttons frame
        action_frame = ttk.LabelFrame(main_frame, text="Contract Operations", padding="5")
        action_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.pledge_btn = ttk.Button(action_frame, text="💰 Support Project", command=self.pledge_dialog, state=tk.DISABLED)
        self.pledge_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.withdraw_btn = ttk.Button(action_frame, text="💸 Withdraw Funds", command=self.withdraw_funds, state=tk.DISABLED)
        self.withdraw_btn.grid(row=0, column=1, padx=(0, 5))
        
        self.refund_btn = ttk.Button(action_frame, text="🔄 Claim Refund", command=self.claim_refund, state=tk.DISABLED)
        self.refund_btn.grid(row=0, column=2, padx=(0, 5))
        
        self.force_update_btn = ttk.Button(action_frame, text="🔄 Force Update", command=self.force_update, state=tk.DISABLED)
        self.force_update_btn.grid(row=0, column=3, padx=(0, 5))
        
        # Balance information
        balance_frame = ttk.LabelFrame(main_frame, text="Wallet Balance", padding="5")
        balance_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(balance_frame, text="Wallet Balance:").grid(row=0, column=0, sticky=tk.W)
        self.wallet_balance_label = ttk.Label(balance_frame, text="0 ETH")
        self.wallet_balance_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # Transaction log frame
        log_frame = ttk.LabelFrame(main_frame, text="Operation Log", padding="5")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=100)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def check_backend_connection(self):
        """Check if backend service is available"""
        try:
            self.log("Checking backend service connection...")
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.backend_available = True
                    self.backend_status_label.config(text="✅ Backend Connected", foreground="green")
                    self.log("✅ Backend service connected successfully")
                    return
            
            self.backend_available = False
            self.backend_status_label.config(text="❌ Backend Unavailable", foreground="red")
            self.log("⚠️ Backend service unavailable, using blockchain directly")
            
        except Exception as e:
            self.backend_available = False
            self.backend_status_label.config(text="❌ Backend Unavailable", foreground="red")
            self.log(f"⚠️ Cannot connect to backend service: {str(e)}")
            self.log("⚠️ Using blockchain directly for data retrieval")
    
    def toggle_backend(self):
        """Toggle between backend API and direct blockchain connection"""
        self.use_backend = not self.use_backend
        
        if self.use_backend and self.backend_available:
            self.backend_toggle_btn.config(text="Switch to Blockchain")
            self.backend_status_label.config(text="✅ Using Backend API", foreground="green")
            self.log("🔄 Switched to Backend API mode")
        else:
            self.backend_toggle_btn.config(text="Switch to Backend")
            self.backend_status_label.config(text="🔗 Using Blockchain Directly", foreground="blue")
            self.log("🔄 Switched to Direct Blockchain mode")
        
        # Refresh data with new mode
        self.refresh_data()
    
    def connect_to_blockchain(self):
        """Connect to blockchain network"""
        self.log("Attempting to connect to blockchain network...")
        
        for i, endpoint in enumerate(self.rpc_endpoints):
            try:
                self.log(f"Trying RPC {i+1}: {endpoint[:50]}...")
                self.w3 = Web3(Web3.HTTPProvider(endpoint))
                
                if self.w3.is_connected():
                    self.current_rpc_index = i
                    network_id = self.w3.eth.chain_id
                    self.log(f"✅ Successfully connected to network! Chain ID: {network_id}")
                    
                    if network_id == 11155111:  # Sepolia chain ID
                        self.network_label.config(text="✅ Connected to Sepolia Testnet", foreground="green")
                        self.rpc_label.config(text=f"RPC: {i+1}/{len(self.rpc_endpoints)}")
                    else:
                        self.network_label.config(text=f"⚠️ Unknown network (Chain ID: {network_id})", foreground="orange")
                    
                    # Initialize contract
                    self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.contract_abi)
                    self.log(f"✅ Contract initialized successfully: {self.contract_address}")
                    
                    # Auto connect default wallet
                    self.connect_default_wallet()
                    return
                    
            except Exception as e:
                self.log(f"❌ RPC {i+1} connection failed: {str(e)}")
                continue
        
        # All RPCs failed
        self.network_label.config(text="❌ Unable to connect to any network", foreground="red")
        self.log("❌ All RPC endpoints failed, please check network connection")
        messagebox.showerror("Connection Error", "Unable to connect to any blockchain network. Please check:\n1. Network connection\n2. RPC endpoint configuration\n3. Firewall settings")
    
    def connect_default_wallet(self):
        """Connect default wallet (using private key from env file)"""
        try:
            if not self.default_private_key:
                self.log("❌ No default private key set")
                messagebox.showwarning("Warning", "No default wallet private key set")
                return
            
            self.account = self.w3.eth.account.from_key(self.default_private_key)
            self.status_label.config(text=f"✅ Connected: {self.account.address[:10]}...")
            self.connect_btn.config(state=tk.DISABLED)
            self.log(f"✅ Default wallet connected: {self.account.address}")
            
            # Update wallet balance
            self.update_wallet_balance()
            # Refresh contract data
            self.refresh_data()
            
        except Exception as e:
            self.log(f"❌ Wallet connection error: {str(e)}")
            messagebox.showerror("Error", f"Wallet connection failed: {str(e)}")
    
    def connect_custom_wallet(self):
        """Connect other wallet"""
        from tkinter import simpledialog
        
        try:
            private_key = simpledialog.askstring("Enter Private Key", 
                                               "Please enter wallet private key:", 
                                               show='*')
            if private_key:
                # Remove possible prefix
                private_key = private_key.strip()
                if private_key.startswith('0x'):
                    private_key = private_key[2:]
                
                self.account = self.w3.eth.account.from_key(private_key)
                self.status_label.config(text=f"✅ Connected: {self.account.address[:10]}...")
                self.log(f"✅ Custom wallet connected: {self.account.address}")
                
                # Update wallet balance
                self.update_wallet_balance()
                # Refresh contract data
                self.refresh_data()
                
        except Exception as e:
            self.log(f"❌ Custom wallet connection error: {str(e)}")
            messagebox.showerror("Error", f"Wallet connection failed: {str(e)}")
    
    def update_wallet_balance(self):
        """Update wallet balance display"""
        if not self.account:
            return
            
        try:
            balance = self.w3.eth.get_balance(self.account.address)
            balance_eth = self.w3.from_wei(balance, 'ether')
            self.wallet_balance_label.config(text=f"{balance_eth:.6f} ETH")
        except Exception as e:
            self.log(f"Balance check error: {str(e)}")
    
    def refresh_data(self):
        """Refresh crowdfunding data - use backend if available"""
        if not self.contract:
            return
            
        try:
            self.log("🔄 Refreshing contract data...")
            
            # If backend is available and enabled, use it for faster data retrieval
            if self.use_backend and self.backend_available:
                threading.Thread(target=self._refresh_from_backend, daemon=True).start()
            else:
                # Backend unavailable or disabled, use blockchain directly
                threading.Thread(target=self._refresh_data_thread, daemon=True).start()
                
        except Exception as e:
            self.log(f"❌ Data refresh error: {str(e)}")
    
    def _refresh_from_backend(self):
        """Get data from backend API"""
        try:
            self.log("📡 Fetching data from backend API...")
            
            # Get campaign status from backend
            response = requests.get(f"{self.backend_url}/campaign/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Convert data format to match frontend UI expectations
                ui_data = {
                    'goal': data['goal'],
                    'raised': data['raised'],
                    'progress': data['progress'],
                    'deadline': data['deadline'],
                    'status': data['status'],
                    'creator': data['creator'],
                    'balance': data.get('contract_balance', 0),
                    'goal_reached': "Yes" if data['goal_reached'] else "No",
                    'funds_withdrawn': "Yes" if data['funds_withdrawn'] else "No",
                    'time_remaining': "From Backend API"
                }
                
                self.root.after(0, self._update_ui, ui_data)
                self.log("✅ Data retrieved from backend API successfully")
                return
            
            # If backend fails, fallback to blockchain
            self.log("⚠️ Backend API request failed, falling back to blockchain")
            self._refresh_data_thread()
            
        except Exception as e:
            self.log(f"❌ Backend API error: {str(e)}, falling back to blockchain")
            self._refresh_data_thread()
    
    def _refresh_data_thread(self):
        """Refresh data in background thread - direct blockchain connection"""
        try:
            # Get contract data directly from blockchain
            goal = self.contract.functions.goal().call()
            amount_raised = self.contract.functions.amountRaised().call()
            deadline = self.contract.functions.deadline().call()
            goal_reached = self.contract.functions.goalReached().call()
            funds_withdrawn = self.contract.functions.fundsWithdrawn().call()
            creator = self.contract.functions.creator().call()
            status = self.contract.functions.getStatus().call()
            contract_balance = self.contract.functions.getContractBalance().call()
            
            # Calculate progress
            progress = (amount_raised / goal) * 100 if goal > 0 else 0
            
            # Convert time
            deadline_date = datetime.fromtimestamp(deadline)
            time_remaining = deadline_date - datetime.now()
            
            # Update UI in main thread
            self.root.after(0, self._update_ui, {
                'goal': self.w3.from_wei(goal, 'ether'),
                'raised': self.w3.from_wei(amount_raised, 'ether'),
                'progress': progress,
                'deadline': deadline_date.strftime("%Y-%m-%d %H:%M:%S"),
                'time_remaining': str(time_remaining).split('.')[0],
                'status': status,
                'creator': creator,
                'balance': self.w3.from_wei(contract_balance, 'ether'),
                'goal_reached': "Yes" if goal_reached else "No",
                'funds_withdrawn': "Yes" if funds_withdrawn else "No"
            })
            
        except Exception as e:
            self.root.after(0, self.log, f"❌ Blockchain data fetch error: {str(e)}")
    
    def _update_ui(self, data):
        """Update UI display"""
        try:
            self.goal_label.config(text=f"{data['goal']:.4f} ETH")
            self.raised_label.config(text=f"{data['raised']:.4f} ETH")
            self.progress_label.config(text=f"{data['progress']:.2f}%")
            self.deadline_label.config(text=f"{data['deadline']} ({data['time_remaining']} remaining)")
            self.status_label.config(text=data['status'])
            self.creator_label.config(text=f"{data['creator'][:10]}...{data['creator'][-8:]}")
            self.balance_label.config(text=f"{data['balance']:.4f} ETH")
            self.goal_reached_label.config(text=data['goal_reached'])
            self.withdrawn_label.config(text=data['funds_withdrawn'])
            
            # Update progress bar
            self.progress_bar['value'] = data['progress']
            
            # Update button states
            is_creator = self.account and self.account.address.lower() == data['creator'].lower()
            is_active = data['status'] == "ACTIVE"
            is_success = data['status'] == "SUCCESS"
            is_failed = data['status'] == "FAILED"
            
            self.pledge_btn.config(state=tk.NORMAL if (is_active and self.account) else tk.DISABLED)
            self.withdraw_btn.config(state=tk.NORMAL if (is_success and is_creator and data['funds_withdrawn'] == "No") else tk.DISABLED)
            self.refund_btn.config(state=tk.NORMAL if (is_failed and float(data['raised']) > 0 and self.account) else tk.DISABLED)
            self.force_update_btn.config(state=tk.NORMAL if self.account else tk.DISABLED)
            
            self.log("✅ Data refresh completed")
            
        except Exception as e:
            self.log(f"❌ UI update error: {str(e)}")
    
    def send_transaction(self, function_call, value=0):
        """Unified transaction sending function with compatibility fixes"""
        try:
            # Build transaction
            transaction = function_call.build_transaction({
                'from': self.account.address,
                'value': value,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            
            # Compatible with different web3.py versions
            if hasattr(signed_txn, 'rawTransaction'):
                raw_tx = signed_txn.rawTransaction
            elif hasattr(signed_txn, 'raw_transaction'):
                raw_tx = signed_txn.raw_transaction
            else:
                # Final attempt to access directly
                try:
                    raw_tx = signed_txn.rawTransaction
                except:
                    raw_tx = signed_txn.raw_transaction
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(raw_tx)
            return tx_hash
            
        except Exception as e:
            raise e
    
    def pledge_dialog(self):
        """Support project dialog"""
        if not self.account:
            messagebox.showwarning("Warning", "Please connect wallet first")
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title("Support Project")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Enter support amount (ETH):", font=("Arial", 10)).pack(pady=10)
        
        amount_var = tk.StringVar()
        amount_entry = ttk.Entry(dialog, textvariable=amount_var, width=20, font=("Arial", 12))
        amount_entry.pack(pady=10)
        
        # Show current balance
        try:
            balance = self.w3.eth.get_balance(self.account.address)
            balance_eth = self.w3.from_wei(balance, 'ether')
            balance_label = ttk.Label(dialog, text=f"Current balance: {balance_eth:.6f} ETH", foreground="gray")
            balance_label.pack(pady=5)
        except:
            pass
        
        def confirm_pledge():
            try:
                amount = float(amount_var.get())
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than 0")
                    return
                    
                # Check if balance is sufficient
                if balance_eth < amount:
                    messagebox.showerror("Error", "Insufficient balance")
                    return
                    
                dialog.destroy()
                self.pledge(amount)
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Confirm Support", command=confirm_pledge).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        amount_entry.focus()
    
    def pledge(self, amount_eth):
        """Support project - using unified transaction function"""
        try:
            amount_wei = self.w3.to_wei(amount_eth, 'ether')
            self.log(f"🔄 Preparing to support {amount_eth} ETH...")
            
            # Use unified transaction sending function
            tx_hash = self.send_transaction(
                self.contract.functions.fund(), 
                value=amount_wei
            )
            
            self.log(f"✅ Support transaction sent: {tx_hash.hex()}")
            messagebox.showinfo("Success", f"Support transaction sent!\n\nTransaction Hash:\n{tx_hash.hex()}")
            self.wait_for_transaction(tx_hash, "Support")
            
        except Exception as e:
            self.log(f"❌ Support error: {str(e)}")
            messagebox.showerror("Error", f"Support failed: {str(e)}")
    
    def withdraw_funds(self):
        """Withdraw funds - using unified transaction function"""
        if not self.account:
            messagebox.showwarning("Warning", "Please connect wallet first")
            return
            
        try:
            self.log("🔄 Preparing to withdraw funds...")
            
            tx_hash = self.send_transaction(self.contract.functions.withdrawFunds())
            
            self.log(f"✅ Withdraw funds transaction sent: {tx_hash.hex()}")
            messagebox.showinfo("Success", f"Withdraw funds transaction sent!\n\nTransaction Hash:\n{tx_hash.hex()}")
            self.wait_for_transaction(tx_hash, "Withdraw Funds")
            
        except Exception as e:
            self.log(f"❌ Withdraw funds error: {str(e)}")
            messagebox.showerror("Error", f"Withdraw funds failed: {str(e)}")
    
    def claim_refund(self):
        """Claim refund - using unified transaction function"""
        if not self.account:
            messagebox.showwarning("Warning", "Please connect wallet first")
            return
            
        try:
            self.log("🔄 Preparing to claim refund...")
            
            tx_hash = self.send_transaction(self.contract.functions.claimRefund())
            
            self.log(f"✅ Refund transaction sent: {tx_hash.hex()}")
            messagebox.showinfo("Success", f"Refund transaction sent!\n\nTransaction Hash:\n{tx_hash.hex()}")
            self.wait_for_transaction(tx_hash, "Refund")
            
        except Exception as e:
            self.log(f"❌ Refund error: {str(e)}")
            messagebox.showerror("Error", f"Refund failed: {str(e)}")
    
    def force_update(self):
        """Force update status - using unified transaction function"""
        if not self.account:
            messagebox.showwarning("Warning", "Please connect wallet first")
            return
            
        try:
            self.log("🔄 Forcing contract status update...")
            
            tx_hash = self.send_transaction(self.contract.functions.forceUpdate())
            
            self.log(f"✅ Status update transaction sent: {tx_hash.hex()}")
            messagebox.showinfo("Success", f"Status update transaction sent!\n\nTransaction Hash:\n{tx_hash.hex()}")
            self.wait_for_transaction(tx_hash, "Status Update")
            
        except Exception as e:
            self.log(f"❌ Status update error: {str(e)}")
            messagebox.showerror("Error", f"Status update failed: {str(e)}")
    
    def wait_for_transaction(self, tx_hash, operation_name):
        """Wait for transaction confirmation"""
        def wait_thread():
            try:
                self.log(f"⏳ Waiting for {operation_name} transaction confirmation...")
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                
                if receipt.status == 1:
                    self.log(f"✅ {operation_name} transaction confirmed successfully!")
                    # Refresh data
                    time.sleep(2)  # Give nodes time to update state
                    self.refresh_data()
                    self.update_wallet_balance()
                else:
                    self.log(f"❌ {operation_name} transaction failed!")
                    
            except Exception as e:
                self.log(f"❌ Transaction confirmation error: {str(e)}")
        
        threading.Thread(target=wait_thread, daemon=True).start()
    
    def log(self, message):
        """Add log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        print(log_entry.strip())

def main():
    root = tk.Tk()
    app = CrowdfundingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()