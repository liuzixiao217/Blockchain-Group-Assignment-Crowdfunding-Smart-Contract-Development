Requirements
Python Version
Python 3.7 or higher

pip install -r requirements.txt
Or
pip install web3 requests fastapi uvicorn pydantic

Blockchain Configuration
Network: Sepolia Test Network
RPC Endpoints: Multiple backup RPCs configured
Contract Address: 0x25D1Cb8E516750F8265329e86cD51d35D6C9C9D4
Wallet Configuration
Important: For security, use environment variables or config files to manage private keys
Method 1: Environment Variables (Recommended)

Step 1: Start Backend Service
Open Terminal/Command Prompt
Navigate to Project Directory
Run Backend Service: python app.py
Verify Backend Running:
◦ Service starts at: http://127.0.0.1:8000
◦ API Documentation: http://127.0.0.1:8000/docs
◦ Health Check: http://127.0.0.1:8000/api/health
Step 2: Start Frontend Application
Open New Terminal/Command Prompt
Navigate to Project Directory
Run Frontend Application: python crowdfunding_app.py
1. Connect Wallet
• Default Wallet: Automatically uses configured private key
• Other Wallet: Click "Use Other Wallet" to enter private key
• Wallet Status: Shows connection status and balance
2. View Crowdfunding Information
Frontend displays:
• Crowdfunding goal and current progress
• Deadline and remaining time
• Project status (ACTIVE/SUCCESS/FAILED)
• Contract creator and balance
• Whether goal is reached
• Whether funds are withdrawn
3. Available Operations
 Support Project
• Available during active project period
• Enter ETH amount to contribute
• Transaction confirmation required
Withdraw Funds
• Available only to project creator
• Available after project success and funds not withdrawn
Claim Refund
• Available when project fails
• Contributors can claim refunds
Force Update
• Manually update contract status
4. Backend Features
Backend provides these API endpoints

Troubleshooting
Common Issues
Blockchain Connection Failed
Check network connection
Verify RPC endpoints are available
Confirm Sepolia testnet access

Backend Won't Start
Check if port 8000 is occupied
Verify Python dependencies installed correctly
Confirm sufficient system permissions


Frontend Cannot Connect to Backend
Confirm backend service is running
Check firewall settings
Verify backend URL configuration

Transaction Failures
Check wallet balance is sufficient
Confirm gas fees are set appropriately
Verify contract status allows the operation
Logs
Backend Logs: View in terminal running backend
Frontend Logs: View in "Operation Log" area of application interface
Security Warnings
Important Security Notes:
Private Key Protection: Never hardcode private keys, use environment variables
Test Network: Use only on test networks, never use mainnet private keys
Fund Safety: Use only test ETH, never real funds
Network Security: Run application in secure environment
Development Notes
Custom Configuration
You can modify:
contract_address: Contract address
rpc_endpoints: List of RPC endpoints
backend_url: Backend API address
Private key management method
Feature Extensions
Possible enhancements:
Add multi-contract support
Implement user authentication
Add more data analytics
Support other blockchain networks
Technical Support
If you encounter issues:
Check log outputs
Verify network connection
Confirm configuration is correct
Check API documentation
Note: This is an educational project. Use only in test environments, not for production or handling real funds.



