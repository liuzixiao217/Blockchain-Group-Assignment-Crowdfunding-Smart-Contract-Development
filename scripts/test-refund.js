const { ethers } = require("hardhat");

async function main() {
  console.log("=== Refund Function Test ===");
  
  const contractAddress = "0x25D1Cb8E516750F8265329e86cD51d35D6C9C9D4";
  const Crowdfunding = await ethers.getContractFactory("CompleteCrowdfunding");
  const contract = Crowdfunding.attach(contractAddress);
  
  const [deployer] = await ethers.getSigners();
  
  console.log("Waiting for campaign deadline...");
  
  // Check campaign status
  const status = await contract.getStatus();
  const deadline = await contract.deadline();
  const currentTime = Math.floor(Date.now() / 1000);
  
  console.log("Current Status:", status);
  console.log("Deadline:", new Date(Number(deadline) * 1000).toLocaleString());
  console.log("Current Time:", new Date(currentTime * 1000).toLocaleString());
  
  if (status === "FAILED") {
    console.log("\nCampaign ended without reaching goal, testing refund...");
    
    // Check current account's contribution
    const contribution = await contract.contributions(deployer.address);
    console.log("Current Account Contribution:", ethers.formatEther(contribution), "ETH");
    
    if (contribution > 0) {
      try {
        console.log("Claiming refund...");
        const tx = await contract.claimRefund();
        await tx.wait();
        console.log("✅ Refund Successful!");
      } catch (error) {
        console.log("❌ Refund Failed:", error.message);
      }
    } else {
      console.log("Current account has no contributions, cannot test refund");
    }
  } else {
    console.log("Campaign not ended yet, please wait for deadline to test refund");
  }
}

main().catch(console.error);