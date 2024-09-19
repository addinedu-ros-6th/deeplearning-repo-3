-- MySQL dump 10.13  Distrib 8.0.39, for Linux (x86_64)
--
-- Host: localhost    Database: deep_project
-- ------------------------------------------------------
-- Server version	8.0.39-0ubuntu0.22.04.1

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
-- Table structure for table `DrivingLog`
--

DROP TABLE IF EXISTS `DrivingLog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DrivingLog` (
  `id` int NOT NULL AUTO_INCREMENT,
  `speed` int DEFAULT NULL,
  `distance` int DEFAULT NULL,
  `time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `DrivingLog`
--

LOCK TABLES `DrivingLog` WRITE;
/*!40000 ALTER TABLE `DrivingLog` DISABLE KEYS */;
INSERT INTO `DrivingLog` VALUES (1,60,10,'2024-09-01 13:12:12'),(2,12,2,'2024-09-02 13:12:12'),(3,255,5,'2024-09-03 13:12:12');
/*!40000 ALTER TABLE `DrivingLog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `EventLog`
--

DROP TABLE IF EXISTS `EventLog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `EventLog` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category` varchar(16) DEFAULT NULL,
  `type` varchar(16) DEFAULT NULL,
  `occurTime` datetime DEFAULT NULL,
  `mid` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `mid` (`mid`),
  CONSTRAINT `EventLog_ibfk_1` FOREIGN KEY (`mid`) REFERENCES `LogMessage` (`id`),
  CONSTRAINT `EventLog_ibfk_2` FOREIGN KEY (`mid`) REFERENCES `LogMessage` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `EventLog`
--

LOCK TABLES `EventLog` WRITE;
/*!40000 ALTER TABLE `EventLog` DISABLE KEYS */;
INSERT INTO `EventLog` VALUES (1,'장애물','test','2024-09-12 11:24:47',2),(5,'표지판','사람','2024-09-12 17:18:30',3),(6,'표지판','사람','2024-09-12 17:19:19',3),(7,'장애물','사람','2024-09-13 13:55:17',2),(8,'장애물','사람','2024-09-13 14:19:00',2);
/*!40000 ALTER TABLE `EventLog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `LogMessage`
--

DROP TABLE IF EXISTS `LogMessage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `LogMessage` (
  `id` int NOT NULL,
  `text` varchar(64) DEFAULT NULL,
  `type` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `LogMessage`
--

LOCK TABLES `LogMessage` WRITE;
/*!40000 ALTER TABLE `LogMessage` DISABLE KEYS */;
INSERT INTO `LogMessage` VALUES (1,'전방 사람 발견 - 서행하세요','person'),(2,'전방 개 발견 - 서행하세요','dog'),(3,'전방 정지 표지판 발견 - 서행하세요','stop'),(4,'전방 50km 표지판 발견 - 시속 50km 이하로 서행하세요','50km'),(5,'전방 50km 해제 표지판 발견 - 속도 제한이 해제되었어요','50km_deactive'),(6,'전방 어린이보호구역 표지판 발견 - 30km이하로 서행하세요','stop'),(7,'전방 어린이보호구역 해제표지판 발견 - 어린이보호구역이 해제되었어요','stop_deactive'),(8,'전방 신호등 빨간불 발견 - 서행 후 멈추세요','Red_sign'),(9,'전방 신호등 초록불 발견 - 출발하세요','Blue_sign');
/*!40000 ALTER TABLE `LogMessage` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-09-19 10:56:16
