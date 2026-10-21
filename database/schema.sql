-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: university_event_management
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `achievements`
--

DROP TABLE IF EXISTS `achievements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `achievements` (
  `achievement_id` int NOT NULL AUTO_INCREMENT,
  `club_id` int DEFAULT NULL,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `achievement_date` date DEFAULT NULL,
  `created_by` int NOT NULL,
  `status` enum('PUBLISHED','ARCHIVED') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'PUBLISHED',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`achievement_id`),
  KEY `fk_achievement_creator` (`created_by`),
  KEY `fk_achievements_club` (`club_id`),
  CONSTRAINT `fk_achievement_creator` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_achievements_club` FOREIGN KEY (`club_id`) REFERENCES `clubs` (`club_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `achievements`
--

LOCK TABLES `achievements` WRITE;
/*!40000 ALTER TABLE `achievements` DISABLE KEYS */;
INSERT INTO `achievements` VALUES (1,1,'Successfully Organized BUP CSE FEST 2026','BUP Computer Programming Club successfully organized BUP CSE FEST 2026 on 29-30 September 2026 at BUP Campus. More than 2,000 students participated in Hackathon, Capture The Flag (CTF), Intra-BUP Competitive Programming and Gaming.','2026-09-30',4,'PUBLISHED','2026-10-08 19:51:48','2026-10-08 19:51:48'),(2,1,'Successfully Organized BUP CSE Tech Carnival 2025','BUP Computer Programming Club successfully organized BUP CSE Tech Carnival 2025 on 24-25 September 2025 at BUP Campus. The carnival featured Competitive Programming, Capture The Flag, Hackathon and FIFA Gaming with participation from universities across Bangladesh.','2025-09-25',4,'PUBLISHED','2026-10-08 19:52:05','2026-10-08 19:52:05');
/*!40000 ALTER TABLE `achievements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `activity_logs`
--

DROP TABLE IF EXISTS `activity_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activity_logs` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `action` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `entity_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `entity_id` int DEFAULT NULL,
  `details` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`),
  KEY `fk_activity_user` (`user_id`),
  CONSTRAINT `fk_activity_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activity_logs`
--

LOCK TABLES `activity_logs` WRITE;
/*!40000 ALTER TABLE `activity_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `activity_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `club_application_answers`
--

DROP TABLE IF EXISTS `club_application_answers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `club_application_answers` (
  `answer_id` int NOT NULL AUTO_INCREMENT,
  `application_id` int DEFAULT NULL,
  `membership_id` int DEFAULT NULL,
  `question_id` int NOT NULL,
  `answer_text` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`answer_id`),
  UNIQUE KEY `uq_membership_question` (`membership_id`,`question_id`),
  UNIQUE KEY `uq_application_question` (`application_id`,`question_id`),
  KEY `fk_application_answer_question` (`question_id`),
  CONSTRAINT `fk_application_answer_membership` FOREIGN KEY (`membership_id`) REFERENCES `club_memberships` (`membership_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_application_answer_question` FOREIGN KEY (`question_id`) REFERENCES `club_application_questions` (`question_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_application_answers_application` FOREIGN KEY (`application_id`) REFERENCES `club_applications` (`application_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `club_application_answers`
--

LOCK TABLES `club_application_answers` WRITE;
/*!40000 ALTER TABLE `club_application_answers` DISABLE KEYS */;
INSERT INTO `club_application_answers` VALUES (1,1,NULL,2,'Yes','2026-10-17 14:30:53','2026-10-17 14:30:53'),(2,1,NULL,3,'Yes','2026-10-17 14:30:53','2026-10-17 14:30:53');
/*!40000 ALTER TABLE `club_application_answers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `club_application_questions`
--

DROP TABLE IF EXISTS `club_application_questions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `club_application_questions` (
  `question_id` int NOT NULL AUTO_INCREMENT,
  `club_id` int NOT NULL,
  `question_text` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `question_type` enum('SHORT_TEXT','LONG_TEXT','YES_NO','SINGLE_CHOICE') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'SHORT_TEXT',
  `options_json` text COLLATE utf8mb4_unicode_ci,
  `is_required` tinyint(1) NOT NULL DEFAULT '1',
  `sort_order` int NOT NULL DEFAULT '1',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_by` int DEFAULT NULL,
  `updated_by` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`question_id`),
  KEY `fk_application_question_club` (`club_id`),
  KEY `fk_application_question_created_by` (`created_by`),
  KEY `fk_application_question_updated_by` (`updated_by`),
  CONSTRAINT `fk_application_question_club` FOREIGN KEY (`club_id`) REFERENCES `clubs` (`club_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_application_question_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_application_question_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `club_application_questions`
--

LOCK TABLES `club_application_questions` WRITE;
/*!40000 ALTER TABLE `club_application_questions` DISABLE KEYS */;
INSERT INTO `club_application_questions` VALUES (1,1,'Why do you want to join BUP Computer Programming Club ?','SHORT_TEXT',NULL,1,1,0,5,5,'2026-10-10 08:06:51','2026-10-11 08:13:09'),(2,1,'do you want to join this club?','YES_NO',NULL,1,2,1,5,5,'2026-10-11 07:30:59','2026-10-11 07:30:59'),(3,1,'ABC?','YES_NO',NULL,1,3,1,5,5,'2026-10-11 08:12:58','2026-10-11 08:12:58');
/*!40000 ALTER TABLE `club_application_questions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `club_applications`
--

DROP TABLE IF EXISTS `club_applications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `club_applications` (
  `application_id` int NOT NULL AUTO_INCREMENT,
  `club_id` int NOT NULL,
  `student_user_id` int NOT NULL,
  `status` enum('DRAFT','PENDING','APPROVED','REJECTED','WITHDRAWN') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'DRAFT',
  `submitted_at` timestamp NULL DEFAULT NULL,
  `withdrawn_at` timestamp NULL DEFAULT NULL,
  `reviewed_by` int DEFAULT NULL,
  `reviewed_at` timestamp NULL DEFAULT NULL,
  `rejection_reason` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`application_id`),
  KEY `fk_club_applications_club` (`club_id`),
  KEY `fk_club_applications_student` (`student_user_id`),
  KEY `fk_club_applications_reviewer` (`reviewed_by`),
  CONSTRAINT `fk_club_applications_club` FOREIGN KEY (`club_id`) REFERENCES `clubs` (`club_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_club_applications_reviewer` FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_club_applications_student` FOREIGN KEY (`student_user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `club_applications`
--

LOCK TABLES `club_applications` WRITE;
/*!40000 ALTER TABLE `club_applications` DISABLE KEYS */;
INSERT INTO `club_applications` VALUES (1,1,7,'PENDING','2026-10-17 14:30:53',NULL,NULL,NULL,NULL,'2026-10-17 14:30:53','2026-10-17 14:30:53');
/*!40000 ALTER TABLE `club_applications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `club_leadership`
--

DROP TABLE IF EXISTS `club_leadership`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `club_leadership` (
  `leadership_id` int NOT NULL AUTO_INCREMENT,
  `club_id` int NOT NULL,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role_title` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `academic_designation` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `department` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `image_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `profile_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sort_order` int DEFAULT '1',
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`leadership_id`),
  KEY `fk_club_leadership_club` (`club_id`),
  CONSTRAINT `fk_club_leadership_club` FOREIGN KEY (`club_id`) REFERENCES `clubs` (`club_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `club_leadership`
--

LOCK TABLES `club_leadership` WRITE;
/*!40000 ALTER TABLE `club_leadership` DISABLE KEYS */;
INSERT INTO `club_leadership` VALUES (1,1,'RUMANA YASMIN','Club Moderator','Lecturer','Department of Computer Science and Engineering, Faculty of Science & Technology (FST)','rumana.yasmin@bup.edu.bd','images/leadership/rumana-yasmin.png','https://bup.edu.bd/faculty-member/details/705',1,1,'2026-10-08 18:58:59','2026-10-08 19:14:10');
/*!40000 ALTER TABLE `club_leadership` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `club_memberships`
--

DROP TABLE IF EXISTS `club_memberships`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `club_memberships` (
  `membership_id` int NOT NULL AUTO_INCREMENT,
  `club_id` int NOT NULL,
  `student_id` int NOT NULL,
  `status` enum('PENDING','APPROVED','REJECTED','INACTIVE') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'PENDING',
  `requested_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `reviewed_by` int DEFAULT NULL,
  `reviewed_at` timestamp NULL DEFAULT NULL,
  `joined_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`membership_id`),
  UNIQUE KEY `uq_student_club` (`student_id`,`club_id`),
  KEY `fk_membership_club` (`club_id`),
  KEY `fk_membership_reviewer` (`reviewed_by`),
  CONSTRAINT `fk_membership_club` FOREIGN KEY (`club_id`) REFERENCES `clubs` (`club_id`),
  CONSTRAINT `fk_membership_reviewer` FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_membership_student` FOREIGN KEY (`student_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `club_memberships`
--

LOCK TABLES `club_memberships` WRITE;
/*!40000 ALTER TABLE `club_memberships` DISABLE KEYS */;
INSERT INTO `club_memberships` VALUES (1,1,3,'APPROVED','2026-10-08 16:13:18',5,'2026-10-09 16:11:56','2026-10-09 16:11:56');
/*!40000 ALTER TABLE `club_memberships` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `club_moderators`
--

DROP TABLE IF EXISTS `club_moderators`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `club_moderators` (
  `moderator_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `club_id` int NOT NULL,
  `assigned_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`moderator_id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `fk_club_moderator_club` (`club_id`),
  CONSTRAINT `fk_club_moderator_club` FOREIGN KEY (`club_id`) REFERENCES `clubs` (`club_id`),
  CONSTRAINT `fk_club_moderator_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `club_moderators`
--

LOCK TABLES `club_moderators` WRITE;
/*!40000 ALTER TABLE `club_moderators` DISABLE KEYS */;
INSERT INTO `club_moderators` VALUES (1,5,1,'2026-10-09 07:27:06',1);
/*!40000 ALTER TABLE `club_moderators` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clubs`
--

DROP TABLE IF EXISTS `clubs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clubs` (
  `club_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `category` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `history` text COLLATE utf8mb4_unicode_ci,
  `requirements` text COLLATE utf8mb4_unicode_ci,
  `status` enum('ACTIVE','INACTIVE') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'ACTIVE',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `website_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `facebook_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mission` text COLLATE utf8mb4_unicode_ci,
  `vision` text COLLATE utf8mb4_unicode_ci,
  `motto` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `administered_by` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`club_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clubs`
--

LOCK TABLES `clubs` WRITE;
/*!40000 ALTER TABLE `clubs` DISABLE KEYS */;
INSERT INTO `clubs` VALUES (1,'BUP Computer Programming Club','The BUP Computer Programming Club focuses on computer science, programming and cybersecurity. It provides workshops, competitions, mentorship and practical learning opportunities for students.','Programming & Technology','Founded in January 2024, the club was established to advance students knowledge and practical skills in computer science and cybersecurity.','Interested BUP students can apply for membership. Membership approval will be handled through the club membership process.','ACTIVE','2026-10-08 15:59:43','2026-10-08 19:34:29','https://www.bup.edu.bd/club-home/bup-computer-programming-club','https://www.facebook.com/bupcopc','To cultivate technical expertise, foster teamwork, and instill a commitment to excellence, particularly in programming and cybersecurity, empowering members for success in the tech industry.','To transform learners into proficient, inventive technologists dedicated to ethical conduct, embracing diversity, and making a positive societal contribution, while shaping the future of technology responsibly.','Code, Compete, Conquer','Department of Computer Science and Engineering, Faculty of Science & Technology (FST)'),(2,'BUP Robotics CLUB','BUP Robotics CLUB focuses on robotics, automation, practical projects, research and technical innovation. The club helps students develop hands-on technical skills beyond academic learning.','Robotics & Technology','BUP Robotics CLUB was founded on 13 September 2017 by enthusiastic undergraduate students from the Department of Information and Communication Technology at BUP.','Interested BUP students can apply for membership. Membership approval will be handled through the club membership process.','ACTIVE','2026-10-08 16:31:57','2026-10-08 16:31:57',NULL,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `clubs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `event_gallery`
--

DROP TABLE IF EXISTS `event_gallery`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `event_gallery` (
  `gallery_id` int NOT NULL AUTO_INCREMENT,
  `event_id` int NOT NULL,
  `image_url` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `caption` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sort_order` int DEFAULT '1',
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`gallery_id`),
  KEY `fk_event_gallery_event` (`event_id`),
  CONSTRAINT `fk_event_gallery_event` FOREIGN KEY (`event_id`) REFERENCES `events` (`event_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event_gallery`
--

LOCK TABLES `event_gallery` WRITE;
/*!40000 ALTER TABLE `event_gallery` DISABLE KEYS */;
/*!40000 ALTER TABLE `event_gallery` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `events`
--

DROP TABLE IF EXISTS `events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `events` (
  `event_id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `event_type` enum('UNIVERSITY','CLUB') COLLATE utf8mb4_unicode_ci NOT NULL,
  `club_id` int DEFAULT NULL,
  `event_date` date NOT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `location` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` int NOT NULL,
  `status` enum('UPCOMING','COMPLETED','CANCELLED') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'UPCOMING',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `image_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `source_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`event_id`),
  KEY `fk_event_club` (`club_id`),
  KEY `fk_event_creator` (`created_by`),
  CONSTRAINT `fk_event_club` FOREIGN KEY (`club_id`) REFERENCES `clubs` (`club_id`),
  CONSTRAINT `fk_event_creator` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `chk_event_club` CHECK ((((`event_type` = _utf8mb4'UNIVERSITY') and (`club_id` is null)) or ((`event_type` = _utf8mb4'CLUB') and (`club_id` is not null))))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `events`
--

LOCK TABLES `events` WRITE;
/*!40000 ALTER TABLE `events` DISABLE KEYS */;
INSERT INTO `events` VALUES (1,'Programming Workshop 2026','A programming workshop for BUP students organized by BUP Computer Programming Club.','CLUB',1,'2026-10-20','10:00:00','13:00:00','BUP Campus',3,'UPCOMING','2026-10-08 17:34:29','2026-10-08 17:34:29',NULL,NULL),(2,'Planning Ahead: Higher Studies in Computer Science and Engineering','BUP Computer Programming Club organized a lecture on higher studies in Computer Science and Engineering. The session covered graduate study opportunities, scholarships, career strategies and preparation for the global technology landscape.','CLUB',1,'2025-05-22',NULL,NULL,'Shadhinota Auditorium, BUP',4,'COMPLETED','2026-10-09 05:23:28','2026-10-09 05:28:13','images/activities/higher-studies-lecture-2025.jpg','https://www.bup.edu.bd/public/news/details/665');
/*!40000 ALTER TABLE `events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `news`
--

DROP TABLE IF EXISTS `news`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `news` (
  `news_id` int NOT NULL AUTO_INCREMENT,
  `reporter_id` int NOT NULL,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` enum('DRAFT','PENDING','PUBLISHED','REJECTED') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'DRAFT',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `submitted_at` timestamp NULL DEFAULT NULL,
  `published_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`news_id`),
  KEY `fk_news_reporter` (`reporter_id`),
  CONSTRAINT `fk_news_reporter` FOREIGN KEY (`reporter_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `news`
--

LOCK TABLES `news` WRITE;
/*!40000 ALTER TABLE `news` DISABLE KEYS */;
/*!40000 ALTER TABLE `news` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `news_reviews`
--

DROP TABLE IF EXISTS `news_reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `news_reviews` (
  `review_id` int NOT NULL AUTO_INCREMENT,
  `news_id` int NOT NULL,
  `authority_id` int NOT NULL,
  `decision` enum('APPROVED','REJECTED') COLLATE utf8mb4_unicode_ci NOT NULL,
  `remarks` text COLLATE utf8mb4_unicode_ci,
  `reviewed_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`review_id`),
  KEY `fk_news_review_news` (`news_id`),
  KEY `fk_news_review_authority` (`authority_id`),
  CONSTRAINT `fk_news_review_authority` FOREIGN KEY (`authority_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `fk_news_review_news` FOREIGN KEY (`news_id`) REFERENCES `news` (`news_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `news_reviews`
--

LOCK TABLES `news_reviews` WRITE;
/*!40000 ALTER TABLE `news_reviews` DISABLE KEYS */;
/*!40000 ALTER TABLE `news_reviews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notices`
--

DROP TABLE IF EXISTS `notices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notices` (
  `notice_id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `notice_type` enum('UNIVERSITY','CLUB') COLLATE utf8mb4_unicode_ci NOT NULL,
  `club_id` int DEFAULT NULL,
  `created_by` int NOT NULL,
  `status` enum('PUBLISHED','ARCHIVED') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'PUBLISHED',
  `published_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`notice_id`),
  KEY `fk_notice_club` (`club_id`),
  KEY `fk_notice_creator` (`created_by`),
  CONSTRAINT `fk_notice_club` FOREIGN KEY (`club_id`) REFERENCES `clubs` (`club_id`),
  CONSTRAINT `fk_notice_creator` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`),
  CONSTRAINT `chk_notice_club` CHECK ((((`notice_type` = _utf8mb4'UNIVERSITY') and (`club_id` is null)) or ((`notice_type` = _utf8mb4'CLUB') and (`club_id` is not null))))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notices`
--

LOCK TABLES `notices` WRITE;
/*!40000 ALTER TABLE `notices` DISABLE KEYS */;
INSERT INTO `notices` VALUES (1,'Programming Workshop Notice','BUP Computer Programming Club will organize a programming workshop for interested students.','CLUB',1,3,'PUBLISHED','2026-10-08 17:03:18','2026-10-08 17:03:18','2026-10-08 17:03:18');
/*!40000 ALTER TABLE `notices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `notification_id` int NOT NULL AUTO_INCREMENT,
  `recipient_id` int NOT NULL,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reference_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reference_id` int DEFAULT NULL,
  `is_read` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`notification_id`),
  KEY `fk_notification_recipient` (`recipient_id`),
  CONSTRAINT `fk_notification_recipient` FOREIGN KEY (`recipient_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `role_id` int NOT NULL AUTO_INCREMENT,
  `role_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`role_id`),
  UNIQUE KEY `role_name` (`role_name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (5,'ADMIN'),(2,'AUTHORITY'),(3,'CLUB_MODERATOR'),(4,'REPORTER'),(1,'STUDENT');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_experiences`
--

DROP TABLE IF EXISTS `student_experiences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_experiences` (
  `experience_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `organization_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role_title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `experience_type` enum('JOB','INTERNSHIP','VOLUNTEER','CLUB','FREELANCE','OTHER') COLLATE utf8mb4_unicode_ci DEFAULT 'OTHER',
  `description` text COLLATE utf8mb4_unicode_ci,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `is_current` tinyint(1) DEFAULT '0',
  `sort_order` int DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`experience_id`),
  KEY `fk_student_experience_user` (`user_id`),
  CONSTRAINT `fk_student_experience_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_experiences`
--

LOCK TABLES `student_experiences` WRITE;
/*!40000 ALTER TABLE `student_experiences` DISABLE KEYS */;
/*!40000 ALTER TABLE `student_experiences` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_professional_profiles`
--

DROP TABLE IF EXISTS `student_professional_profiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_professional_profiles` (
  `professional_profile_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `profile_photo` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bio` text COLLATE utf8mb4_unicode_ci,
  `skills` text COLLATE utf8mb4_unicode_ci,
  `github_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `linkedin_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `facebook_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `portfolio_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cv_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`professional_profile_id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `fk_student_professional_profile_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_professional_profiles`
--

LOCK TABLES `student_professional_profiles` WRITE;
/*!40000 ALTER TABLE `student_professional_profiles` DISABLE KEYS */;
INSERT INTO `student_professional_profiles` VALUES (1,3,'uploads/profile_photos/4d9b2db65c494bdf94bb89191a7365c4.jpeg',NULL,NULL,'https://github.com/yourusername','https://linkedin.com/in/yourusername','https://facebook.com/yourusername','https://yourportfolio.com',NULL,'2026-10-21 08:54:15','2026-10-21 09:43:11');
/*!40000 ALTER TABLE `student_professional_profiles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_profile_achievements`
--

DROP TABLE IF EXISTS `student_profile_achievements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_profile_achievements` (
  `achievement_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `achievement_title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `achievement_type` enum('AWARD','CERTIFICATION','COMPETITION','PUBLICATION','SCHOLARSHIP','OTHER') COLLATE utf8mb4_unicode_ci DEFAULT 'OTHER',
  `organization_name` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `achievement_date` date DEFAULT NULL,
  `credential_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sort_order` int DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`achievement_id`),
  KEY `fk_student_profile_achievement_user` (`user_id`),
  CONSTRAINT `fk_student_profile_achievement_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_profile_achievements`
--

LOCK TABLES `student_profile_achievements` WRITE;
/*!40000 ALTER TABLE `student_profile_achievements` DISABLE KEYS */;
/*!40000 ALTER TABLE `student_profile_achievements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_profiles`
--

DROP TABLE IF EXISTS `student_profiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_profiles` (
  `user_id` int NOT NULL,
  `student_id` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `department` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `batch` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `student_id` (`student_id`),
  CONSTRAINT `fk_student_profile_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_profiles`
--

LOCK TABLES `student_profiles` WRITE;
/*!40000 ALTER TABLE `student_profiles` DISABLE KEYS */;
INSERT INTO `student_profiles` VALUES (3,'23456789','ict','24'),(6,'233442','CSE','24'),(7,'2334421','ict','24');
/*!40000 ALTER TABLE `student_profiles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_projects`
--

DROP TABLE IF EXISTS `student_projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_projects` (
  `project_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `project_title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `project_description` text COLLATE utf8mb4_unicode_ci,
  `technologies` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `project_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `github_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `is_ongoing` tinyint(1) DEFAULT '0',
  `sort_order` int DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`project_id`),
  KEY `fk_student_project_user` (`user_id`),
  CONSTRAINT `fk_student_project_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_projects`
--

LOCK TABLES `student_projects` WRITE;
/*!40000 ALTER TABLE `student_projects` DISABLE KEYS */;
/*!40000 ALTER TABLE `student_projects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `role_id` int NOT NULL,
  `full_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`),
  KEY `fk_users_role` (`role_id`),
  CONSTRAINT `fk_users_role` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (3,1,'Tanvir Islam Riyad','riyadtanvirislam47@gmail.com','scrypt:32768:8:1$PdrXC195ym4rHDl4$ec39b6c0eae5557b35b7c073828351be43fc4c4ecc0841010e64c8bf187802f72b16f0e41427c5b4fae0a99b666acde31ba8f39cf7093f48e19a34b44632789c','0193728964398',1,'2026-10-07 18:25:24','2026-10-07 18:25:24'),(4,2,'BUP Authority Test','authority.test@bup.local','pbkdf2:sha256:600000$bupauthority2026$bb1499453abdbd0ffdeba553b74cf08240e96c2bdf412a1dfd76ffc2b6ebbddb',NULL,1,'2026-10-08 19:50:41','2026-10-08 19:50:41'),(5,3,'CPC Moderator Test','moderator.cpc@bup.local','scrypt:32768:8:1$OGFSgWN7QsaYQQyj$eef33da5401b95a02dc591081475a0e852e2d6b2181db4d6d6b03aaf4af4019bed5bffdc747654bad8851a10f4d3c7b37f97172ac176ca21b02579bb1d06b1ec',NULL,1,'2026-10-09 07:27:05','2026-10-09 07:27:05'),(6,1,'AB','riyad123@gmail.com','scrypt:32768:8:1$aWWjT2pybS5YQaBx$92a35523f8fbcf02612273a5e69f3fd44ce5dfa3b7771462350b015d3b7c443e2e785a0e7f3cffd585b503f6d59714ee8b597aeb053380d3cc16ae1fc9613116','0173456677',1,'2026-10-10 15:18:02','2026-10-10 15:18:02'),(7,1,'Ab','abc12@gmail.com','scrypt:32768:8:1$fKC7YUi9r5ZYyu6N$ef7c24566a4c33a16c0d2152a977763820cc00f023c93bcc429e93198be0762640cea26635298140894edfe827f62fd4b4b98d5252a99256cfbca7719e3324a0','+8801852876716',1,'2026-10-17 14:16:09','2026-10-17 14:16:09');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-21 19:10:20
