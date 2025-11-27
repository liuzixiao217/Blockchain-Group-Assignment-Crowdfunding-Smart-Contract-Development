const { ethers } = require("hardhat");

async function main() {
  console.log("🔍 Check Contract Status");
  
  const contractAddress = "0x25D1Cb8E516750F8265329e86cD51d35D6C9C9D4";
  
  try {
    const [deployer] = await ethers.getSigners();
    console.log("👤 Checking Account:", deployer.address);
    
    const Crowdfunding = await ethers.getContractFactory("CompleteCrowdfunding");
    const contract = Crowdfunding.attach(contractAddress);
    
    console.log("📍 Contract Address:", contractAddress);
    
    const creator = await contract.creator();
    const goal = await contract.goal();
    const amountRaised = await contract.amountRaised();
    const goalReached = await contract.goalReached();
    const fundsWithdrawn = await contract.fundsWithdrawn();
    const deadline = await contract.deadline();
    const status = await contract.getStatus();
    const contractBalance = await contract.getContractBalance();
    const contributorCount = await contract.getContributorCount();
    
    console.log("\n📊 Contract Status:");
    console.log("Creator:", creator);
    console.log("Goal Amount:", ethers.formatEther(goal), "ETH");
    console.log("Amount Raised:", ethers.formatEther(amountRaised), "ETH");
    console.log("Goal Reached:", goalReached);
    console.log("Funds Withdrawn:", fundsWithdrawn);
    console.log("Status:", status);
    console.log("Contract Balance:", ethers.formatEther(contractBalance), "ETH");
    console.log("Contributor Count:", contributorCount.toString());
    
    const currentTime = Math.floor(Date.now() / 1000);
    const timeLeft = Number(deadline) - currentTime;
    const minutesLeft = Math.floor(timeLeft / 60);
    const secondsLeft = timeLeft % 60;
    
    console.log("\n⏰ Time Information:");
    console.log("Time Remaining:", minutesLeft, "minutes", secondsLeft, "seconds");
    console.log("Deadline:", new Date(Number(deadline) * 1000).toLocaleString());
    
    console.log("\n🌐 View Links:");
    console.log("Etherscan: https://sepolia.etherscan.io/address/" + contractAddress);
    
    console.log("\n💡 Next Steps:");
    if (status === "ACTIVE" && !goalReached && timeLeft > 0) {
      console.log("Run: npx hardhat run reach-goal-quick.js --network sepolia");
    } else if (status === "SUCCESS" && !fundsWithdrawn) {
      console.log("Run: npx hardhat run test-withdraw-final.js --network sepolia");
    } else if (status === "FAILED") {
      console.log("Contract failed, you can test refund function");
    }
    
  } catch (error) {
    console.error("❌ Check Failed:", error.message);
  }
}

main();