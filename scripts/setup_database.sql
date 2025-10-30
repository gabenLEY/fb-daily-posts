-- PostgreSQL Database Setup Script
-- Run these commands in PostgreSQL as a superuser (postgres)

-- Create user
CREATE USER fb_posts_user WITH PASSWORD '125689Gby1$1';

-- Create database
CREATE DATABASE fb_posts_db OWNER fb_posts_user;

-- Grant all privileges on database
GRANT ALL PRIVILEGES ON DATABASE fb_posts_db TO fb_posts_user;

-- Connect to the database and grant schema privileges
\c fb_posts_db;
GRANT ALL ON SCHEMA public TO fb_posts_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO fb_posts_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO fb_posts_user;

-- Show confirmation
SELECT 'Database and user created successfully!' as status;