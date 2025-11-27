// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract CompleteCrowdfunding {
    address public creator;
    uint256 public goal;
    uint256 public deadline;
    uint256 public amountRaised;
    bool public goalReached;
    bool public fundsWithdrawn;
    
    mapping(address => uint256) public contributions;
    address[] public contributors;
    
    event Funded(address backer, uint256 amount);
    event GoalAchieved(uint256 total);
    event FundsWithdrawn(address creator, uint256 amount);
    event RefundClaimed(address backer, uint256 amount);

    constructor(uint256 _goal, uint256 _duration) {
        creator = msg.sender;
        goal = _goal;
        deadline = block.timestamp + _duration;
        amountRaised = 0;
        goalReached = false;
        fundsWithdrawn = false;
    }

    function fund() public payable {
        require(block.timestamp < deadline, "Campaign ended");
        require(!goalReached, "Goal already reached");
        require(msg.value > 0, "No zero value");
        
        if (contributions[msg.sender] == 0) {
            contributors.push(msg.sender);
        }
        
        amountRaised += msg.value;
        contributions[msg.sender] += msg.value;
        
        if (amountRaised >= goal && !goalReached) {
            goalReached = true;
            emit GoalAchieved(amountRaised);
        }
        
        emit Funded(msg.sender, msg.value);
    }

    function withdrawFunds() public {
        require(msg.sender == creator, "Only creator can withdraw");
        require(goalReached, "Goal not reached");
        require(!fundsWithdrawn, "Funds already withdrawn");
        require(address(this).balance > 0, "No funds to withdraw");
        
        fundsWithdrawn = true;
        uint256 amount = address(this).balance;
        
        (bool success, ) = creator.call{value: amount}("");
        require(success, "Transfer failed");
        
        emit FundsWithdrawn(creator, amount);
    }

    function claimRefund() public {
        require(block.timestamp > deadline, "Campaign not ended");
        require(!goalReached, "Goal reached, no refunds");
        require(contributions[msg.sender] > 0, "No contribution to refund");
        
        uint256 amountToRefund = contributions[msg.sender];
        contributions[msg.sender] = 0;
        
        (bool success, ) = msg.sender.call{value: amountToRefund}("");
        require(success, "Refund transfer failed");
        
        emit RefundClaimed(msg.sender, amountToRefund);
    }

    function batchRefund(uint256 startIndex, uint256 endIndex) public {
        require(block.timestamp > deadline, "Campaign not ended");
        require(!goalReached, "Goal reached, no refunds");
        require(startIndex < endIndex && endIndex <= contributors.length, "Invalid index range");
        
        for (uint256 i = startIndex; i < endIndex; i++) {
            address contributor = contributors[i];
            uint256 contribution = contributions[contributor];
            
            if (contribution > 0) {
                contributions[contributor] = 0;
                
                (bool success, ) = contributor.call{value: contribution}("");
                require(success, "Batch refund transfer failed");
                
                emit RefundClaimed(contributor, contribution);
            }
        }
    }

    function getStatus() public view returns (string memory) {
        if (goalReached) return "SUCCESS";
        if (block.timestamp > deadline) return "FAILED";
        return "ACTIVE";
    }
    
    function getContractBalance() public view returns (uint256) {
        return address(this).balance;
    }
    
    function getContributorCount() public view returns (uint256) {
        return contributors.length;
    }

    function forceUpdate() public {
        if (amountRaised >= goal && !goalReached) {
            goalReached = true;
            emit GoalAchieved(amountRaised);
        }
    }

    receive() external payable {
        fund();
    }
}