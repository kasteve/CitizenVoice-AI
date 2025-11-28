-- Create Database
CREATE DATABASE CitizenVoiceAI;
GO

USE CitizenVoiceAI;
GO

-- Citizens Table
CREATE TABLE Citizens (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(200) NOT NULL,
    phone NVARCHAR(15) UNIQUE NOT NULL,
    email NVARCHAR(100),
    district NVARCHAR(100),
    created_at DATETIME DEFAULT GETDATE()
);

-- Policies Table
CREATE TABLE Policies (
    id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(500) NOT NULL,
    description NVARCHAR(MAX),
    category NVARCHAR(100),
    status NVARCHAR(50) DEFAULT 'Draft',
    created_at DATETIME DEFAULT GETDATE(),
    deadline DATETIME
);

-- Policy Feedback Table
CREATE TABLE PolicyFeedback (
    id INT IDENTITY(1,1) PRIMARY KEY,
    policy_id INT FOREIGN KEY REFERENCES Policies(id),
    citizen_id INT FOREIGN KEY REFERENCES Citizens(id),
    feedback_text NVARCHAR(MAX),
    sentiment NVARCHAR(20),
    themes NVARCHAR(MAX),
    submitted_at DATETIME DEFAULT GETDATE()
);

-- Complaints Table
CREATE TABLE Complaints (
    id INT IDENTITY(1,1) PRIMARY KEY,
    citizen_id INT FOREIGN KEY REFERENCES Citizens(id),
    category NVARCHAR(100),
    description NVARCHAR(MAX),
    location NVARCHAR(200),
    priority NVARCHAR(20),
    status NVARCHAR(50) DEFAULT 'Pending',
    tracking_number NVARCHAR(50) UNIQUE,
    created_at DATETIME DEFAULT GETDATE(),
    resolved_at DATETIME
);

-- Service Ratings Table
CREATE TABLE ServiceRatings (
    id INT IDENTITY(1,1) PRIMARY KEY,
    citizen_id INT FOREIGN KEY REFERENCES Citizens(id),
    service_type NVARCHAR(100),
    service_location NVARCHAR(200),
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment NVARCHAR(MAX),
    created_at DATETIME DEFAULT GETDATE()
);

-- USSD Sessions Table
CREATE TABLE USSDSessions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    session_id NVARCHAR(100) UNIQUE,
    phone_number NVARCHAR(15),
    current_menu NVARCHAR(50),
    data NVARCHAR(MAX),
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);

GO