# 🚀 HoosHelper: Deployment Guide

**Production-ready deployment options for your hackathon project**

Since you mentioned you don't need Docker or Vercel deployment, this guide focuses on alternative deployment strategies.

---

## 🎯 Quick Deployment Options

### Option 1: Railway (Easiest)
**Time**: 15 minutes  
**Cost**: Free tier available  
**Best for**: Quick hackathon deploys

### Option 2: Render
**Time**: 20 minutes  
**Cost**: Free tier available  
**Best for**: Simple full-stack apps

### Option 3: Traditional VPS (DigitalOcean, Linode)
**Time**: 45 minutes  
**Cost**: $5-12/month  
**Best for**: Full control

---

## 📦 Option 1: Railway Deployment

Railway provides free hosting for full-stack apps with PostgreSQL.

### Step 1: Database Setup

1. Go to [railway.app](https://railway.app)
2. Create new project → Add PostgreSQL
3. Go to PostgreSQL service → Variables
4. Copy `DATABASE_URL`
5. Connect and run:

```sql
CREATE EXTENSION vector;
```

### Step 2: Backend Deployment

1. In Railway dashboard → New Service → GitHub Repo
2. Select your repository
3. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. Add environment variables:
```
DATABASE_URL=<from PostgreSQL service>
DIRECT_URL=<same as DATABASE_URL>
OPENAI_API_KEY=<your key>
ANTHROPIC_API_KEY=<your key>
PORT=8000
```

5. Deploy! Note the URL (e.g., `https://your-app.railway.app`)

### Step 3: Frontend Deployment

1. New Service → GitHub Repo (same repo)
2. Configure:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npx prisma generate && npm run build`
   - **Start Command**: `npm start`

3. Add environment variables:
```
DATABASE_URL=<from PostgreSQL service>
DIRECT_URL=<same as DATABASE_URL>
NEXT_PUBLIC_API_URL=<backend URL from step 2>
```

4. Deploy! Your app is live!

---

## 📦 Option 2: Render Deployment

Render offers free hosting with easy setup.

### Step 1: Database

1. Go to [render.com](https://render.com)
2. New → PostgreSQL
3. Name: `hooshelper-db`
4. Free tier is fine
5. Copy Internal Database URL
6. Connect via psql and run:

```sql
CREATE EXTENSION vector;
```

### Step 2: Backend Web Service

1. New → Web Service
2. Connect your GitHub repository
3. Configure:
   - **Name**: `hooshelper-backend`
   - **Root Directory**: `backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. Environment Variables:
```
DATABASE_URL=<from database>
DIRECT_URL=<from database>
OPENAI_API_KEY=<your key>
ANTHROPIC_API_KEY=<your key>
PYTHON_VERSION=3.11
```

5. Create service

### Step 3: Frontend Web Service

1. New → Web Service
2. Same repository
3. Configure:
   - **Name**: `hooshelper-frontend`
   - **Root Directory**: `frontend`
   - **Environment**: Node
   - **Build Command**: `npm install && npx prisma generate && npm run build`
   - **Start Command**: `npm start`

4. Environment Variables:
```
DATABASE_URL=<from database>
DIRECT_URL=<from database>
NEXT_PUBLIC_API_URL=<backend URL>
NODE_VERSION=18
```

5. Create service

---

## 📦 Option 3: VPS Deployment (DigitalOcean/Linode)

Full control with a traditional server.

### Step 1: Create Droplet/Linode

1. Choose Ubuntu 22.04 LTS
2. At least 2GB RAM ($12/month)
3. Add SSH key
4. Create

### Step 2: Initial Server Setup

SSH into server:

```bash
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y nodejs npm python3 python3-pip python3-venv postgresql postgresql-contrib nginx

# Install pgvector
apt install -y postgresql-server-dev-all
cd /tmp
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
make install
```

### Step 3: Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL:
CREATE DATABASE hooshelper;
CREATE USER hooshelper WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE hooshelper TO hooshelper;
\c hooshelper
CREATE EXTENSION vector;
\q
```

### Step 4: Deploy Backend

```bash
# Create app directory
mkdir -p /var/www/hooshelper
cd /var/www/hooshelper

# Clone repo
git clone https://github.com/yourusername/hooshelper.git .

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://hooshelper:your-secure-password@localhost:5432/hooshelper
DIRECT_URL=postgresql://hooshelper:your-secure-password@localhost:5432/hooshelper
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
BACKEND_PORT=8000
EOF

# Test backend
python main.py
# Press Ctrl+C after verifying it starts
```

### Step 5: Deploy Frontend

```bash
cd /var/www/hooshelper/frontend

# Install dependencies
npm install

# Create .env.local
cat > .env.local << EOF
DATABASE_URL=postgresql://hooshelper:your-secure-password@localhost:5432/hooshelper
DIRECT_URL=postgresql://hooshelper:your-secure-password@localhost:5432/hooshelper
NEXT_PUBLIC_API_URL=http://your-server-ip:8000
EOF

# Generate Prisma client and push schema
npx prisma generate
npx prisma db push

# Build
npm run build

# Test
npm start
# Press Ctrl+C after verifying
```

### Step 6: Process Management with systemd

Create backend service:

```bash
sudo nano /etc/systemd/system/hooshelper-backend.service
```

```ini
[Unit]
Description=HoosHelper Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/hooshelper/backend
Environment="PATH=/var/www/hooshelper/backend/venv/bin"
ExecStart=/var/www/hooshelper/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Create frontend service:

```bash
sudo nano /etc/systemd/system/hooshelper-frontend.service
```

```ini
[Unit]
Description=HoosHelper Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/hooshelper/frontend
ExecStart=/usr/bin/npm start
Restart=always
Environment=NODE_ENV=production
Environment=PORT=3000

[Install]
WantedBy=multi-user.target
```

Enable and start services:

```bash
sudo systemctl daemon-reload
sudo systemctl enable hooshelper-backend
sudo systemctl enable hooshelper-frontend
sudo systemctl start hooshelper-backend
sudo systemctl start hooshelper-frontend

# Check status
sudo systemctl status hooshelper-backend
sudo systemctl status hooshelper-frontend
```

### Step 7: Nginx Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/hooshelper
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/hooshelper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 8: SSL with Let's Encrypt (Optional)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 🔐 Environment Variables Reference

### Backend (.env)
```bash
DATABASE_URL="postgresql://user:pass@host:5432/db?pgbouncer=true"
DIRECT_URL="postgresql://user:pass@host:5432/db"
OPENAI_API_KEY="sk-..."
ANTHROPIC_API_KEY="sk-ant-..."
BACKEND_PORT=8000
FRONTEND_URL="https://your-domain.com"
```

### Frontend (.env.local)
```bash
DATABASE_URL="postgresql://user:pass@host:5432/db?pgbouncer=true"
DIRECT_URL="postgresql://user:pass@host:5432/db"
NEXT_PUBLIC_API_URL="https://api.your-domain.com"
```

---

## 🧪 Testing Deployment

### Backend Health Check

```bash
curl https://your-backend-url.com/
# Should return: {"status":"healthy","service":"HoosHelper API","version":"1.0.0"}
```

### Frontend Check

Visit your frontend URL in browser. All pages should load.

### Database Connection

```bash
curl -X GET https://your-backend-url.com/api/courses
# Should return JSON with courses
```

---

## 📊 Monitoring & Logs

### Railway
- Dashboard shows logs automatically
- Metrics tab shows usage

### Render
- Logs tab in each service
- Metrics available in dashboard

### VPS
```bash
# Backend logs
sudo journalctl -u hooshelper-backend -f

# Frontend logs
sudo journalctl -u hooshelper-frontend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🐛 Troubleshooting

### "Database connection failed"

Check connection string format:
```
postgresql://username:password@host:port/database
```

For Supabase/pgvector, you might need:
```
postgresql://username:password@host:port/database?pgbouncer=true
```

### "Module not found" errors

```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
npx prisma generate
```

### "Port already in use"

```bash
# Find process
sudo lsof -i :8000  # Backend
sudo lsof -i :3000  # Frontend

# Kill process
kill -9 <PID>
```

### "CORS errors"

Update `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-url.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🔄 Updating Deployment

### Railway/Render (Auto-deploy)

Just push to GitHub:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

Platforms auto-deploy on push.

### VPS (Manual)

```bash
ssh root@your-server-ip
cd /var/www/hooshelper
git pull

# Backend
sudo systemctl restart hooshelper-backend

# Frontend (rebuild required)
cd frontend
npm run build
sudo systemctl restart hooshelper-frontend
```

---

## 💰 Cost Estimates

### Free Tier Options
- **Railway**: Free for first 500 hours/month
- **Render**: Free tier with limitations
- **Supabase**: Free tier (500MB database)

### Paid Options
- **Railway**: ~$5-20/month
- **Render**: ~$7-15/month
- **VPS**: $5-12/month (DigitalOcean, Linode)
- **Supabase Pro**: $25/month

### API Costs
- **OpenAI**: ~$0.10-1.00 per 1000 queries
- **Anthropic**: ~$3.00 per million tokens

**Total estimated cost**: $10-30/month for production use

---

## 🎯 Post-Deployment Checklist

- [ ] All pages load without errors
- [ ] Course data is populated
- [ ] Plan validation works
- [ ] Chat returns responses
- [ ] Clubs page loads
- [ ] API calls succeed
- [ ] No console errors
- [ ] Mobile responsive
- [ ] SSL certificate active (if using custom domain)
- [ ] Monitoring setup
- [ ] Backup strategy in place

---

## 📈 Scaling Considerations

### When You Need to Scale

Signs you need more resources:
- Response time > 2 seconds
- Database CPU > 80%
- Memory usage > 90%
- 500+ concurrent users

### Scaling Strategies

1. **Database**: Upgrade to larger instance, add read replicas
2. **Backend**: Horizontal scaling with load balancer
3. **Frontend**: CDN for static assets
4. **Caching**: Redis for API responses

---

## 🔒 Security Best Practices

### Required
- [ ] Use HTTPS (SSL certificate)
- [ ] Environment variables for secrets (never commit .env)
- [ ] Database uses strong passwords
- [ ] API rate limiting enabled
- [ ] CORS configured properly

### Recommended
- [ ] Regular backups of database
- [ ] Monitoring and alerts
- [ ] Log sensitive errors only
- [ ] Keep dependencies updated

---

## 📞 Support Resources

- **Railway**: [docs.railway.app](https://docs.railway.app)
- **Render**: [render.com/docs](https://render.com/docs)
- **Supabase**: [supabase.com/docs](https://supabase.com/docs)
- **pgvector**: [github.com/pgvector/pgvector](https://github.com/pgvector/pgvector)

---

**Your app is production-ready! 🚀**

Remember: Start with free tiers, upgrade as you gain users. Good luck!

