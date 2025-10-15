# 🔧 Troubleshooting: Cosmos DB Connection Timeout

**Error**: `timed out (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms)`

This means your code cannot reach the Cosmos DB MongoDB vCore cluster. Here are the solutions:

---

## 🎯 Quick Fixes (Try in Order)

### **Fix 1: Add Your IP to Firewall Rules** ⭐ (Most Common)

Your Cosmos DB cluster is blocking your connection because your IP address isn't whitelisted.

#### Steps in Azure Portal:

1. **Go to Azure Portal** → https://portal.azure.com
2. **Navigate to your Cosmos DB MongoDB vCore cluster**
   - Search for: `fc-e1a5ee2e3ac9-000`
3. **Click on "Networking" or "Firewall"** (left menu)
4. **Add your current IP address:**
   - Option A: Click "Add current client IP address"
   - Option B: Manually add your IP (see below to find it)
5. **Click "Save"**
6. **Wait 2-3 minutes** for changes to propagate

#### Find Your Current IP Address:

```bash
# Run this in your terminal
curl ifconfig.me
```

Or visit: https://whatismyipaddress.com/

---

### **Fix 2: Enable Public Access**

If firewall rules don't work, ensure public access is enabled:

1. **Azure Portal** → Your Cosmos DB cluster
2. **Networking** section
3. **Public network access**: Set to "Enabled"
4. **Firewall rules**: 
   - Add your IP: `xxx.xxx.xxx.xxx`
   - Or temporarily add: `0.0.0.0` - `255.255.255.255` (all IPs - not recommended for production!)
5. **Save** and wait 2-3 minutes

---

### **Fix 3: Check Connection String Format**

Verify your `.env.example` connection string format:

```bash
# View your connection string (password will be masked)
python test_config.py
```

**Correct Format for MongoDB vCore:**
```
mongodb+srv://username:password@fc-e1a5ee2e3ac9-000.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000
```

**Common Issues:**
- ❌ Missing `mongodb+srv://` prefix
- ❌ Incorrect username/password
- ❌ Missing query parameters (`?tls=true&authMechanism=SCRAM-SHA-256`)
- ❌ Extra spaces or line breaks in connection string

#### Get Correct Connection String:

1. **Azure Portal** → Your Cosmos DB MongoDB vCore cluster
2. **Connection strings** (left menu)
3. **Copy** the full connection string
4. **Replace** `<password>` with your actual password
5. **Paste** into `.env` file (single line, no breaks)

---

### **Fix 4: Verify Cluster is Running**

1. **Azure Portal** → Your Cosmos DB cluster
2. Check **Status**: Should be "Ready" or "Running"
3. If status is "Stopped" or "Updating":
   - Wait for it to complete
   - Start the cluster if stopped

---

### **Fix 5: Increase Timeout in Code** (Temporary workaround)

If you're on a slow network, increase the timeout:

Edit `src/vector_db/vector_db/cosmos_vector_db.py`:

```python
# Find this line:
self.client = MongoClient(connection_string)

# Replace with:
self.client = MongoClient(
    connection_string,
    serverSelectionTimeoutMS=60000,  # 60 seconds
    connectTimeoutMS=60000,
    socketTimeoutMS=60000
)
```

---

## 🔍 Diagnostic Commands

Run these to help diagnose the issue:

### **1. Check if DNS resolves:**
```bash
nslookup fc-e1a5ee2e3ac9-000.mongocluster.cosmos.azure.com
```

### **2. Check if port is reachable:**
```bash
nc -zv fc-e1a5ee2e3ac9-000.mongocluster.cosmos.azure.com 10260
```
*Expected: "Connection succeeded"*

### **3. Test with MongoDB URI:**
```bash
# If you have mongosh installed
mongosh "mongodb+srv://username:password@fc-e1a5ee2e3ac9-000.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256"
```

### **4. Check your current IP:**
```bash
curl ifconfig.me
echo ""
```

---

## 📋 Complete Firewall Setup Guide

### **Step-by-Step: Add Your IP to Cosmos DB**

1. **Get your IP address:**
   ```bash
   curl ifconfig.me
   ```
   *Example output: `203.0.113.45`*

2. **Go to Azure Portal:**
   - Navigate to: https://portal.azure.com
   - Search for: `Cosmos DB` or your cluster name

3. **Find your cluster:**
   - Look for cluster starting with: `fc-e1a5ee2e3ac9`
   - Click on it

4. **Configure Networking:**
   - Left menu → Click **"Networking"** or **"Firewall and virtual networks"**
   
5. **Add IP Rule:**
   ```
   Rule Name: My Development Machine
   IP Address: [Your IP from step 1]
   ```
   *Click "+ Add IP address" or "+ Add client IP"*

6. **Save Changes:**
   - Click **"Save"** button (top of page)
   - Wait 2-3 minutes for Azure to apply changes

7. **Test Connection:**
   ```bash
   python test_config.py
   ```

---

## 🚨 Quick Emergency Solution

If you need to test immediately and can't wait:

### **Temporarily Allow All IPs (NOT FOR PRODUCTION!):**

1. Azure Portal → Your Cosmos DB cluster
2. Networking → Firewall
3. Add this rule:
   ```
   Start IP: 0.0.0.0
   End IP: 255.255.255.255
   ```
4. Save and test

⚠️ **WARNING**: This allows anyone to connect! Remove this rule after testing!

---

## ✅ Verification Steps

After applying fixes, test in this order:

```bash
# 1. Test DNS resolution
nslookup fc-e1a5ee2e3ac9-000.mongocluster.cosmos.azure.com

# 2. Test port connectivity
nc -zv fc-e1a5ee2e3ac9-000.mongocluster.cosmos.azure.com 10260

# 3. Test Python connection
python test_config.py

# 4. Try embedding
python embed_documents.py
```

---

## 🎯 Most Likely Solution

**90% of the time**, this is a firewall issue. Here's the fastest fix:

```bash
# 1. Get your IP
curl ifconfig.me

# 2. Go to Azure Portal
# 3. Add this IP to Cosmos DB Networking/Firewall
# 4. Wait 2-3 minutes
# 5. Test again
python test_config.py
```

---

## 📞 Still Having Issues?

Check these common mistakes:

- ❌ **Wrong connection string format**: Must start with `mongodb+srv://`
- ❌ **Password has special characters**: URL-encode them (e.g., `@` → `%40`)
- ❌ **IP changed**: If on home WiFi, your IP might change - re-add it
- ❌ **VPN/Proxy**: Disable VPN and try again
- ❌ **Corporate network**: May block MongoDB ports (10260)
- ❌ **Cluster suspended**: Check cluster status in Azure Portal

---

## 🔐 Connection String Encoding

If your password has special characters, encode them:

| Character | Encoded |
|-----------|---------|
| `@` | `%40` |
| `:` | `%3A` |
| `/` | `%2F` |
| `?` | `%3F` |
| `#` | `%23` |
| `&` | `%26` |

**Example:**
```
Original password: Pass@123!
Encoded password: Pass%40123!

Connection string:
mongodb+srv://admin:Pass%40123!@cluster.cosmos.azure.com/...
```

---

## 📚 Additional Resources

- [Azure Cosmos DB Networking Docs](https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-configure-firewall)
- [MongoDB Connection String Format](https://www.mongodb.com/docs/manual/reference/connection-string/)

---

**Next Step**: Add your IP to the firewall and wait 2-3 minutes, then run:
```bash
python test_config.py
```
