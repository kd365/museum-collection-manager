-- MySQL dump 10.13  Distrib 8.0.43, for Linux (x86_64)
--
-- Host: localhost    Database: museumapp
-- ------------------------------------------------------
-- Server version	8.0.43-0ubuntu0.24.04.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `artists`
--

DROP TABLE IF EXISTS `artists`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `artists` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `birth_date` date DEFAULT NULL,
  `death_date` date DEFAULT NULL,
  `bio` text,
  `art_movement` enum('Renaissance','Baroque','Rococo','Neoclassicism','Romanticism','Realism','Impressionism','Post-Impressionism','Expressionism','Cubism','Surrealism','Abstract Expressionism','Pop Art','Minimalism','Contemporary','Modern','Gothic','Byzantine','Art Nouveau','Art Deco','Dadaism','Fauvism','Futurism','Other','Unknown') DEFAULT NULL,
  `is_living` tinyint(1) DEFAULT '1',
  `birth_place` varchar(100) DEFAULT NULL,
  `death_place` varchar(100) DEFAULT NULL,
  `primary_medium` enum('Painting','Sculpture','Drawing','Printmaking','Photography','Mixed Media','Digital Art','Installation','Performance','Ceramics','Textiles','Collage','Watercolor','Oil Painting','Acrylic','Other') DEFAULT NULL,
  `gender` enum('Male','Female','Other') DEFAULT NULL,
  `notable_works` text,
  `image_url` varchar(255) DEFAULT NULL,
  `portrait_url` varchar(255) DEFAULT NULL,
  `website` varchar(255) DEFAULT NULL,
  `instagram` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `nationality` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `artworks`
--

DROP TABLE IF EXISTS `artworks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `artworks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) DEFAULT NULL,
  `artist_id` int DEFAULT NULL,
  `medium` varchar(100) DEFAULT NULL,
  `creation_date` date DEFAULT NULL,
  `dimension_H` decimal(10,2) DEFAULT NULL,
  `dimension_W` decimal(8,2) DEFAULT NULL,
  `dimension_D` decimal(8,2) DEFAULT NULL,
  `estimated_value` decimal(12,2) DEFAULT NULL,
  `description` text,
  `dimension_unit` enum('inches','cm','meters','feet') DEFAULT 'inches',
  `weight` decimal(10,2) DEFAULT NULL,
  `weight_unit` enum('kg','lbs','grams') DEFAULT 'lbs',
  `art_movement` enum('Renaissance','Baroque','Rococo','Neoclassicism','Romanticism','Realism','Impressionism','Post-Impressionism','Expressionism','Cubism','Surrealism','Abstract Expressionism','Pop Art','Minimalism','Contemporary','Modern','Gothic','Byzantine','Art Nouveau','Art Deco','Dadaism','Fauvism','Futurism','Other','Unknown') DEFAULT NULL,
  `subject` enum('Portrait','Self-Portrait','Landscape','Seascape','Cityscape','Still Life','Religious','Mythology','Historical','Genre Scene','Nude','Animal','Abstract','Floral','Interior','Architectural','Battle Scene','Allegorical','Fantasy','Other','Unknown') DEFAULT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `thumbnail_url` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `provenance` text,
  `is_original` tinyint(1) DEFAULT '1',
  `edition_number` varchar(50) DEFAULT NULL,
  `is_signed` tinyint(1) DEFAULT '0',
  `signature_location` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `artist_id` (`artist_id`),
  CONSTRAINT `artworks_ibfk_1` FOREIGN KEY (`artist_id`) REFERENCES `artists` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `collections`
--

DROP TABLE IF EXISTS `collections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `collections` (
  `id` int NOT NULL AUTO_INCREMENT,
  `museum_id` int DEFAULT NULL,
  `artwork_id` int NOT NULL,
  `accession_number` varchar(50) DEFAULT NULL,
  `acquisition_date` date DEFAULT NULL,
  `acquisition_method` enum('Purchase','Donation','Bequest','Exchange','Commission','Transfer') NOT NULL,
  `acquisition_cost` decimal(12,2) DEFAULT NULL,
  `acquisition_details` text,
  `donor_name` varchar(200) DEFAULT NULL,
  `status` enum('Active','On Loan','In Conservation','Deaccessioned','Storage') DEFAULT 'Active',
  `location_type` enum('Gallery','Storage','Conservation Lab','On Loan','Other') DEFAULT NULL,
  `gallery_location` varchar(100) DEFAULT NULL,
  `storage_location` varchar(100) DEFAULT NULL,
  `on_display` tinyint(1) DEFAULT '0',
  `on_loan` tinyint(1) DEFAULT '0',
  `loan_institution` varchar(200) DEFAULT NULL,
  `loan_start_date` date DEFAULT NULL,
  `loan_end_date` date DEFAULT NULL,
  `current_value` decimal(12,2) DEFAULT NULL,
  `insurance_value` decimal(12,2) DEFAULT NULL,
  `last_appraisal_date` date DEFAULT NULL,
  `condition_status` enum('Excellent','Good','Fair','Poor','Restoration Needed') DEFAULT NULL,
  `last_condition_check` date DEFAULT NULL,
  `conservation_notes` text,
  `provenance` text,
  `deaccession_date` date DEFAULT NULL,
  `deaccession_reason` text,
  `deaccession_method` enum('Sale','Donation','Transfer','Destroyed','Other') DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accession_number` (`accession_number`),
  KEY `museum_id` (`museum_id`),
  KEY `artwork_id` (`artwork_id`),
  CONSTRAINT `collections_ibfk_1` FOREIGN KEY (`museum_id`) REFERENCES `museums` (`id`) ON DELETE CASCADE,
  CONSTRAINT `collections_ibfk_2` FOREIGN KEY (`artwork_id`) REFERENCES `artworks` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `museums`
--

DROP TABLE IF EXISTS `museums`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `museums` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `museum_type` enum('Art','History','Science','Natural History','Archaeology','Modern Art','Other') DEFAULT NULL,
  `address` varchar(200) DEFAULT NULL,
  `city` varchar(100) NOT NULL,
  `state_province` varchar(100) DEFAULT NULL,
  `country` varchar(100) NOT NULL,
  `postal_code` varchar(20) DEFAULT NULL,
  `established_date` date DEFAULT NULL,
  `website` varchar(200) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `description` text,
  `annual_visitors` int DEFAULT NULL,
  `admission_fee` decimal(8,2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-26  5:43:43
