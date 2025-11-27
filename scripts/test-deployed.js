const { ethers } = require("hardhat");

async function main() {
  console.log("=== Test Deployed Crowdfunding Contract ===");
  
  const contractAddress = "0x25D1Cb8E516750F8265329e86cD51d35D6C9C9D4";
  
  console.log("Contract Address:", contractAddress);
  
  try {
    const signers = await ethers.getSigners();
    const deployer = signers[0];
    
    console.log("Current Tester:", deployer.address);
    console.log("Account Balance:", ethers.formatEther(await ethers.provider.getBalance(deployer.address)), "ETH");

    const Crowdfunding = await ethers.getContractFactory("CompleteCrowdfunding");
    const contract = Crowdfunding.attach(contractAddress);
    
    console.log("✅ Successfully connected to contract");

    // 1. Read contract status
    console.log("\n1. Reading Contract Status...");
    const creator = await contract.creator();
    const goal = await contract.goal();
    const amountRaised = await contract.amountRaised();
    const goalReached = await contract.goalReached();
    const fundsWithdrawn = await contract.fundsWithdrawn();
    const deadline = await contract.deadline();
    const status = await contract.getStatus();
    const contractBalance = await contract.getContractBalance();
    const contributorCount = await contract.getContributorCount();
    
    console.log("   Creator:", creator);
    console.log("   Goal Amount:", ethers.formatEther(goal), "ETH");
    console.log("   Amount Raised:", ethers.formatEther(amountRaised), "ETH");
    console.log("   Goal Reached:", goalReached);
    console.log("   Funds Withdrawn:", fundsWithdrawn);
    console.log("   Deadline:", new Date(Number(deadline) * 1000).toLocaleString());
    console.log("   Status:", status);
    console.log("   Contract Balance:", ethers.formatEther(contractBalance), "ETH");
    console.log("   Contributor Count:", contributorCount.toString());

    // 2. Check current time
    const currentTime = Math.floor(Date.now() / 1000);
    const timeLeft = Number(deadline) - currentTime;
    console.log("   Time Remaining:", Math.max(0, timeLeft), "seconds");

    // 3. If contract is active, test funding
    if (status === "ACTIVE") {
      console.log("\n2. Testing Funding Function...");
      
      const myContribution = await contract.contributions(deployer.address);
      console.log("   Current Account Contribution:", ethers.formatEther(myContribution), "ETH");
      
      try {
        const donateAmount = ethers.parseEther("0.0001");
        console.log("   Donation Amount:", ethers.formatEther(donateAmount), "ETH");
        
        const tx = await contract.fund({ value: donateAmount });
        console.log("   Waiting for transaction confirmation...");
        const receipt = await tx.wait();
        
        console.log("   ✅ Donation Successful!");
        console.log("   Transaction Hash:", receipt.hash);
        
        const newAmountRaised = await contract.amountRaised();
        const newGoalReached = await contract.goalReached();
        const newStatus = await contract.getStatus();
        const newContribution = await contract.contributions(deployer.address);
        
        console.log("   Updated Amount Raised:", ethers.formatEther(newAmountRaised), "ETH");
        console.log("   Updated Goal Reached:", newGoalReached);
        console.log("   Updated Status:", newStatus);
        console.log("   Updated Contribution:", ethers.formatEther(newContribution), "ETH");
        
      } catch (error) {
        console.log("   ❌ Donation Failed:", error.message);
      }
    } else {
      console.log("\n2. Contract status is", status, ", skipping donation test");
    }

    // 4. Test other read-only functions
    console.log("\n3. Testing Other Functions...");
    
    if (deployer.address.toLowerCase() === creator.toLowerCase() && goalReached && !fundsWithdrawn) {
      console.log("   Testing Funds Withdrawal...");
      try {
        const withdrawTx = await contract.withdrawFunds();
        await withdrawTx.wait();
        console.log("   ✅ Funds Withdrawal Successful");
      } catch (error) {
        console.log("   ❌ Funds Withdrawal Failed:", error.message);
      }
    }
    
    if (amountRaised >= goal && !goalReached) {
      console.log("   Executing Force Status Update...");
      try {
        const updateTx = await contract.forceUpdate();
        await updateTx.wait();
        console.log("   ✅ Status Update Successful");
      } catch (error) {
        console.log("   ❌ Status Update Failed:", error.message);
      }
    }

    console.log("\n=== Test Completed ===");

  } catch (error) {
    console.error("❌ Test Failed:", error.message);
    process.exitCode = 1;
  }
}

main().catch((error) => {
  console.error("Script Execution Failed:", error);
  process.exitCode = 1;
});