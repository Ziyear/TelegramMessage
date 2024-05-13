CREATE DATABASE tg_message;
USE tg_message;
CREATE TABLE `message` (
                           `id` int(11) NOT NULL AUTO_INCREMENT,
                           `sender_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
                           `sender_name` varchar(255) DEFAULT NULL,
                           `username` varchar(255) DEFAULT NULL,
                           `group_username` varchar(255) DEFAULT NULL,
                           `message` varchar(255) DEFAULT NULL,
                           `send_message` varchar(255) DEFAULT NULL,
                           `send_flag` varchar(255) DEFAULT NULL,
                           `sender` blob,
                           `date_time` datetime DEFAULT NULL,
                           PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
