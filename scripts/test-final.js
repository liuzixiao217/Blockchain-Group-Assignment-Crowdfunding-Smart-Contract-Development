const { ethers } = require("hardhat");

async function main() {
  console.log("=== Complete Crowdfunding Test ===");
  
  try {
    const [deployer] = await ethers.getSigners();
    console.log("Deployer Address:", deployer.address);
    console.log("Account Balance:", ethers.formatEther(await ethers.provider.getBalance(deployer.address)), "ETH");

    // Deploy contract with shorter duration for testing (10 minutes)
    console.log("\nDeploying Contract...");
    const goal = ethers.parseEther("0.001");
    const duration = 10 * 60; // 10 minutes for testing
    
    const Crowdfunding = await ethers.getContractFactory("CompleteCrowdfunding");
    const contract = await Crowdfunding.deploy(goal, duration);
    await contract.waitForDeployment();
    
    const address = await contract.getAddress();
    console.log("✅ Contract Deployed:", address);

    // Test basic functionality
    console.log("\nTesting Basic Functions...");
    
    // 1. Check initial status
    const status = await contract.getStatus();
    console.log("Contract Status:", status);
    
    // 2. Make a contribution
    console.log("Making Contribution...");
    const tx = await contract.fund({ value: ethers.parseEther("0.001") });
    await tx.wait();
    console.log("✅ Contribution Successful");
    
    // 3. Check status after contribution
    const newStatus = await contract.getStatus();
    const raised = await contract.amountRaised();
    const reached = await contract.goalReached();
    
    console.log("Status After Contribution:", newStatus);
    console.log("Amount Raised:", ethers.formatEther(raised), "ETH");
    console.log("Goal Reached:", reached);
    
    // 4. Test withdrawal if goal reached
    if (reached) {
      console.log("\nTesting Withdrawal...");
      const withdrawTx = await contract.withdrawFunds();
      await withdrawTx.wait();
      console.log("✅ Withdrawal Successful");
    }
    
    console.log("\n🎉 All Tests Completed Successfully!");

  } catch (error) {
    console.error("❌ Error:", error.message);
  }
}

main();