-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema moneykeeper
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema moneykeeper
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `moneykeeper` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `moneykeeper` ;

-- -----------------------------------------------------
-- Table `moneykeeper`.`user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `moneykeeper`.`user` (
  `user_id` TINYINT(3) UNSIGNED NOT NULL AUTO_INCREMENT,
  `fname` VARCHAR(45) NOT NULL,
  `lname` VARCHAR(45) NOT NULL,
  `bday` DATE NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE INDEX `user_id_UNIQUE` (`user_id` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `moneykeeper`.`transacion_type`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `moneykeeper`.`transacion_type` (
  `transacion_type_id` INT NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`transacion_type_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `moneykeeper`.`planning_parameter`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `moneykeeper`.`planning_parameter` (
  `pp_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `pp_val` DOUBLE UNSIGNED NOT NULL,
  `date_from` DATE NOT NULL,
  `date_to` DATE NOT NULL,
  `user_user_id` TINYINT(3) UNSIGNED NOT NULL,
  `transacion_type_id` INT NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`pp_id`),
  INDEX `fk_revenue_user1_idx` (`user_user_id` ASC) VISIBLE,
  INDEX `fk_planning_parameter_transacion_type1_idx` (`transacion_type_id` ASC) VISIBLE,
  CONSTRAINT `fk_revenue_user1`
    FOREIGN KEY (`user_user_id`)
    REFERENCES `moneykeeper`.`user` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_planning_parameter_transacion_type1`
    FOREIGN KEY (`transacion_type_id`)
    REFERENCES `moneykeeper`.`transacion_type` (`transacion_type_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `moneykeeper`.`group_goods`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `moneykeeper`.`group_goods` (
  `group_goods_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `transacion_type_id` INT NOT NULL,
  PRIMARY KEY (`group_goods_id`),
  INDEX `fk_group_goods_transacion_type1_idx` (`transacion_type_id` ASC) VISIBLE,
  CONSTRAINT `fk_group_goods_transacion_type1`
    FOREIGN KEY (`transacion_type_id`)
    REFERENCES `moneykeeper`.`transacion_type` (`transacion_type_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `moneykeeper`.`purchase`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `moneykeeper`.`purchase` (
  `purchase_id` INT NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `group_goods_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`purchase_id`),
  INDEX `fk_purchase_group_goods1_idx` (`group_goods_id` ASC) VISIBLE,
  CONSTRAINT `fk_purchase_group_goods1`
    FOREIGN KEY (`group_goods_id`)
    REFERENCES `moneykeeper`.`group_goods` (`group_goods_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `moneykeeper`.`account`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `moneykeeper`.`account` (
  `account_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`account_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `moneykeeper`.`transaction`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `moneykeeper`.`transaction` (
  `transaction_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` TINYINT(3) UNSIGNED NOT NULL,
  `transacion_type_id` INT NOT NULL,
  `purchase_id` INT NOT NULL,
  `date` DATE NOT NULL,
  `value` FLOAT(10,2) NULL DEFAULT 0,
  `account_from_id` INT UNSIGNED NULL DEFAULT 1,
  `comment` VARCHAR(255) NULL,
  `save_money` ENUM('Y', 'N') NULL DEFAULT 'N',
  PRIMARY KEY (`transaction_id`),
  INDEX `fk_transaction_user1_idx` (`user_id` ASC) VISIBLE,
  INDEX `fk_transaction_transacion_type1_idx` (`transacion_type_id` ASC) VISIBLE,
  INDEX `fk_transaction_purchase1_idx` (`purchase_id` ASC) VISIBLE,
  INDEX `fk_transaction_account1_idx` (`account_from_id` ASC) VISIBLE,
  CONSTRAINT `fk_transaction_user1`
    FOREIGN KEY (`user_id`)
    REFERENCES `moneykeeper`.`user` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_transaction_transacion_type1`
    FOREIGN KEY (`transacion_type_id`)
    REFERENCES `moneykeeper`.`transacion_type` (`transacion_type_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_transaction_purchase1`
    FOREIGN KEY (`purchase_id`)
    REFERENCES `moneykeeper`.`purchase` (`purchase_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_transaction_account1`
    FOREIGN KEY (`account_from_id`)
    REFERENCES `moneykeeper`.`account` (`account_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
