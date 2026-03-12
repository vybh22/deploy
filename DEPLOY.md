# Deployment Guide - Render

This guide walks you through deploying ECOFEAST to Render.com.

## Prerequisites
- GitHub account with your repository
- Render.com account (free tier available)
- Google Maps API key (for geolocation features)

## Step 1: Prepare Your Repository

1. Ensure all files are committed to GitHub:
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Important**: Never commit your `.env` file - it should be in `.gitignore`
   ```bash
   echo ".env" >> .gitignore
   git add .gitignore
   git commit -m "Add .env to gitignore"
   git push
   ```

## Step 2: Create PostgreSQL Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `ecofeast-db`
   - **Database**: `ecofeast_prod`
   - **User**: `ecofeast_user`
   - **Region**: Choose closest to your users
   - **Plan**: Free tier (or paid if needed)
4. Click **"Create Database"**
5. Wait for the database to be ready (usually 2-3 minutes)
6. Copy the **Internal Database URL** (you'll need this)

## Step 3: Deploy Backend Service

1. From Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository:
   - Click **"Connect GitHub Account"**
   - Authorize Render
   - Select `foodwastered` repository
3. Configure Service:
   - **Name**: `ecofeast-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python run.py init_db`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT run:app`
   - **Plan**: Free tier (or paid)
   - **Region**: Same as database
   - **Root Directory**: `/backend` ← **IMPORTANT**

4. Add Environment Variables:
   - Click **"Add Environment Variable"** for each:

   | Key | Value |
   |-----|-------|
   | `FLASK_ENV` | `production` |
   | `DATABASE_URL` | Internal PostgreSQL URL (from step 2) |
   | `GOOGLE_MAPS_KEY` | Your Google Maps API key |
   | `SECRET_KEY` | Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
   | `JWT_SECRET_KEY` | Generate another random string |
   | `DEBUG` | `False` |
   | `SESSION_COOKIE_SECURE` | `True` |

5. Click **"Create Web Service"**
6. Render will automatically:
   - Build your application
   - Start the Flask server
   - Assign you a public URL (e.g., `https://ecofeast-backend.onrender.com`)

## Step 4: Setup Frontend (Static Files)

Since your Flask app serves static files, they're already deployed with the backend.

To access your application:
- **Frontend**: `https://ecofeast-backend.onrender.com`
- **API**: `https://ecofeast-backend.onrender.com/api`

## Step 5: Verify Deployment

1. Test the application:
   ```bash
   curl https://ecofeast-backend.onrender.com
   ```

2. Check deployment logs:
   - Render Dashboard → Select your service → **"Logs"**

3. Create admin user:
   - Go to `https://ecofeast-backend.onrender.com/register` as admin
   - Or run via terminal:
     ```bash
     render exec ecofeast-backend python run.py create_admin
     ```

## Step 6: Configure Custom Domain (Optional)

1. In Render Dashboard → Your Service → **"Settings"**
2. Scroll to **"Custom Domain"**
3. Add your domain and follow DNS setup instructions

## Environment Variables Reference

### Required Variables
- `DATABASE_URL`: PostgreSQL connection string (provide this from Render DB)
- `GOOGLE_MAPS_KEY`: Get from [Google Cloud Console](https://console.cloud.google.com)
- `SECRET_KEY`: Random secure string for session management
- `JWT_SECRET_KEY`: Random secure string for JWT tokens

### Optional Variables
- `FLASK_ENV`: Set to `production` for production deployments
- `DEBUG`: Set to `False` in production
- `SESSION_COOKIE_SECURE`: Set to `True` for HTTPS
- `GIT_COMMIT_SHA`: Auto-populated by Render

## Troubleshooting

### Database Connection Error
- Verify `DATABASE_URL` is correct (internal URL for Render databases)
- Check that database is in the same region as web service
- Ensure PostgreSQL service is running

### Application Won't Start
- Check the Logs in Render Dashboard
- Common issues:
  - Missing dependencies → ensure all packages in `requirements.txt`
  - Database not initialized → verify `init_db` command runs
  - Environment variables not set

### Static Files Not Loading
- Verify `FLASK_ENV=production`
- Check that CSS/JS files are in `app/static/`
- Clear browser cache (Ctrl+Shift+Delete)

### Deployment Takes Too Long
- Free tier services auto-spin down after 15 minutes of inactivity
- If your app starts slowly, consider upgrading to a paid plan

### Map Not Displaying
- Verify `GOOGLE_MAPS_KEY` is set in environment variables
- Check that Google Maps API is enabled in your Google Cloud project
- Ensure API key restrictions are set correctly

## Subsequent Deployments

After the initial deployment, any push to your GitHub repository's main branch will automatically:
1. Rebuild the application
2. Run database migrations
3. Deploy new version

To deploy manually:
- Render Dashboard → Your Service → **"Manual Deploy"** → **"Deploy latest commit"**

## Scaling & Optimization

For production use:
- **Upgrade plan**: Free tier is suitable for testing; upgrade for reliability
- **Enable auto-deploy**: Already enabled when connected to GitHub
- **Setup monitoring**: Use Render's built-in monitoring alerts
- **Enable backups**: PostgreSQL free tier doesn't backup; consider paid tier

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [Flask Deployment Best Practices](https://flask.palletsprojects.com/deployment/)
- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-connect-string.html)
