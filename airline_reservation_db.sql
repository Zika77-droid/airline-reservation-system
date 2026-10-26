-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 26, 2026 at 03:15 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `airline_reservation_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `airports`
--

CREATE TABLE `airports` (
  `airport_code` varchar(3) NOT NULL,
  `airport_name` varchar(100) NOT NULL,
  `city` varchar(50) NOT NULL,
  `country` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `airports`
--

INSERT INTO `airports` (`airport_code`, `airport_name`, `city`, `country`) VALUES
('CAI', 'Cairo International Airport', 'Cairo', 'Egypt'),
('CDG', 'Charles de Gaulle Airport', 'Paris', 'France'),
('DOH', 'Hamad International Airport', 'Doha', 'Qatar'),
('DXB', 'Dubai International Airport', 'Dubai', 'UAE'),
('FRA', 'Frankfurt Airport', 'Frankfurt', 'Germany'),
('IST', 'Istanbul Airport', 'Istanbul', 'Turkey'),
('JED', 'King Abdulaziz International Airport', 'Jeddah', 'Saudi Arabia'),
('JFK', 'John F. Kennedy International Airport', 'New York', 'USA'),
('LHR', 'Heathrow Airport', 'London', 'UK'),
('RUH', 'King Khalid International Airport', 'Riyadh', 'Saudi Arabia');

-- --------------------------------------------------------

--
-- Table structure for table `bookings`
--

CREATE TABLE `bookings` (
  `booking_id` int(11) NOT NULL,
  `passenger_id` int(11) NOT NULL,
  `flight_id` int(11) NOT NULL,
  `booking_date` date NOT NULL,
  `status` varchar(20) DEFAULT 'Confirmed'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `bookings`
--

INSERT INTO `bookings` (`booking_id`, `passenger_id`, `flight_id`, `booking_date`, `status`) VALUES
(1, 1, 1, '2026-10-24', 'Confirmed');

-- --------------------------------------------------------

--
-- Table structure for table `flights`
--

CREATE TABLE `flights` (
  `flight_id` int(11) NOT NULL,
  `flight_number` varchar(10) NOT NULL,
  `departure_airport` varchar(3) NOT NULL,
  `arrival_airport` varchar(3) NOT NULL,
  `departure_time` datetime NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `available_seats` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `flights`
--

INSERT INTO `flights` (`flight_id`, `flight_number`, `departure_airport`, `arrival_airport`, `departure_time`, `price`, `available_seats`) VALUES
(1, 'MS777', 'CAI', 'DXB', '2026-11-10 09:30:00', 350.00, 149),
(2, 'EK902', 'DXB', 'LHR', '2026-11-12 14:15:00', 600.00, 200),
(3, 'BA154', 'LHR', 'CAI', '2026-11-15 18:00:00', 450.00, 2),
(4, 'SV301', 'CAI', 'RUH', '2026-11-15 08:00:00', 290.00, 120),
(5, 'MS665', 'CAI', 'JED', '2026-11-18 01:45:00', 270.00, 180),
(6, 'AF503', 'CDG', 'CAI', '2026-11-20 13:20:00', 480.00, 95),
(7, 'MS985', 'CAI', 'JFK', '2026-11-22 23:00:00', 920.00, 110),
(8, 'TK114', 'IST', 'CAI', '2026-11-25 17:30:00', 310.00, 160),
(9, 'QR1302', 'DOH', 'DXB', '2026-11-28 10:00:00', 210.00, 220),
(10, 'LH582', 'FRA', 'CAI', '2026-12-01 15:40:00', 510.00, 85);

-- --------------------------------------------------------

--
-- Table structure for table `passengers`
--

CREATE TABLE `passengers` (
  `passenger_id` int(11) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `passport_number` varchar(20) NOT NULL,
  `phone` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `passengers`
--

INSERT INTO `passengers` (`passenger_id`, `full_name`, `passport_number`, `phone`) VALUES
(1, 'Omar Hassan', 'A12345678', '+201001234567'),
(2, 'Sarah Ahmed', 'B98765432', '+201119876543');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `airports`
--
ALTER TABLE `airports`
  ADD PRIMARY KEY (`airport_code`);

--
-- Indexes for table `bookings`
--
ALTER TABLE `bookings`
  ADD PRIMARY KEY (`booking_id`),
  ADD KEY `passenger_id` (`passenger_id`),
  ADD KEY `flight_id` (`flight_id`);

--
-- Indexes for table `flights`
--
ALTER TABLE `flights`
  ADD PRIMARY KEY (`flight_id`),
  ADD UNIQUE KEY `flight_number` (`flight_number`),
  ADD KEY `departure_airport` (`departure_airport`),
  ADD KEY `arrival_airport` (`arrival_airport`);

--
-- Indexes for table `passengers`
--
ALTER TABLE `passengers`
  ADD PRIMARY KEY (`passenger_id`),
  ADD UNIQUE KEY `passport_number` (`passport_number`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bookings`
--
ALTER TABLE `bookings`
  MODIFY `booking_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `flights`
--
ALTER TABLE `flights`
  MODIFY `flight_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `passengers`
--
ALTER TABLE `passengers`
  MODIFY `passenger_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `bookings`
--
ALTER TABLE `bookings`
  ADD CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`passenger_id`) REFERENCES `passengers` (`passenger_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`flight_id`) REFERENCES `flights` (`flight_id`) ON DELETE CASCADE;

--
-- Constraints for table `flights`
--
ALTER TABLE `flights`
  ADD CONSTRAINT `flights_ibfk_1` FOREIGN KEY (`departure_airport`) REFERENCES `airports` (`airport_code`) ON DELETE CASCADE,
  ADD CONSTRAINT `flights_ibfk_2` FOREIGN KEY (`arrival_airport`) REFERENCES `airports` (`airport_code`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
