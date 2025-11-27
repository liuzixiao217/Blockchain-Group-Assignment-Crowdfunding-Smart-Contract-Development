require("dotenv").config();

function validatePrivateKey(key) {
  if (!key) return "❌ Missing private key";
  if (key.length !== 64) return `❌ Wrong length: ${key.length} chars (should be 64)`;
  if (!/^[0-9a-f]+$/i.test(key)) return "❌ Contains invalid characters";
  return "✅ Valid private key";
}

console.log("Private key check:", validatePrivateKey(process.env.PRIVATE_KEY));
console.log("Key:", process.env.PRIVATE_KEY);