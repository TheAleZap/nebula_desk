USE master;
GO

IF DB_ID('conversation_db') IS NULL
    CREATE DATABASE conversation_db;
GO

IF DB_ID('intelligence_db') IS NULL
    CREATE DATABASE intelligence_db;
GO

IF NOT EXISTS (SELECT 1 FROM sys.sql_logins WHERE name = 'conversation_user')
    CREATE LOGIN conversation_user WITH PASSWORD = 'LocalConversation_2026!';
GO

IF NOT EXISTS (SELECT 1 FROM sys.sql_logins WHERE name = 'intelligence_user')
    CREATE LOGIN intelligence_user WITH PASSWORD = 'LocalIntelligence_2026!';
GO

USE conversation_db;

GO

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'conversation_user')
    CREATE USER conversation_user FOR LOGIN conversation_user;
GO

IF IS_ROLEMEMBER('db_owner', 'conversation_user') <> 1
    ALTER ROLE db_owner ADD MEMBER conversation_user;
GO

USE intelligence_db;
GO

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'intelligence_user')
    CREATE USER intelligence_user FOR LOGIN intelligence_user;
GO

IF IS_ROLEMEMBER('db_owner', 'intelligence_user') <> 1
    ALTER ROLE db_owner ADD MEMBER intelligence_user;
GO
