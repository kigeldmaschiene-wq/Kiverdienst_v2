# 🚀 KIVerdienst v2 - Quick Start Guide

Get up and running in **5 minutes**!

## Step 1: Install (2 minutes)

```bash
cd /opt
sudo git clone <repository-url> kiverdienst_v2
cd kiverdienst_v2
sudo ./install.sh
```

The installer will:
- ✅ Install Docker if missing
- ✅ Generate secure passwords  
- ✅ Start all services
- ✅ Initialize database

## Step 2: Setup Wizard (2 minutes)

Open in your browser:
```
http://YOUR-SERVER-IP:5000/setup
```

Follow the 4-step wizard:
1. **Welcome** - Overview of features
2. **System Check** - Verify everything works
3. **Configuration** - Enter your email and API keys (optional)
4. **Complete** - You're done!

## Step 3: Create Your First Brand (1 minute)

1. Go to **Dashboard → Brands**
2. Click **"Create New Brand"**
3. Fill in:
   - Name: "My TikTok Channel"
   - Niche: "Technology"
   - TikTok Account: "@myhandle"
4. Click **Save**

## 🎉 Done!

You now have:
- ✅ Working KIVerdienst v2 system
- ✅ Web dashboard at port 5000
- ✅ API server at port 8000
- ✅ PostgreSQL database
- ✅ First brand ready to go

## 📍 Important URLs

- **Dashboard:** http://YOUR-IP:5000/dashboard
- **Brands:** http://YOUR-IP:5000/brands
- **Logs:** http://YOUR-IP:5000/logs
- **Debug Tools:** http://YOUR-IP:5000/debug
- **API Docs:** http://YOUR-IP:8000/docs

## 🆘 Quick Help

**Check if everything is running:**
```bash
./scripts/health_check.sh
```

**View logs:**
```bash
docker compose logs -f
```

**Restart services:**
```bash
docker compose restart
```

**Full documentation:** See [README.md](README.md)

---

**That's it!** You're ready to start creating content. 🎬
