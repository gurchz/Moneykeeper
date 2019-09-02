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
-- Table `moneykeeper`.`planning_group`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `moneykeeper`.`planning_group` (
  `pl_gr_id` CHAR(3) NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`pl_gr_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `moneykeeper`.`purchase`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `moneykeeper`.`purchase` (
  `purchase_id` INT NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `group_goods_id` INT UNSIGNED NOT NULL,
  `planning_group_pl_gr_id` CHAR(3) NOT NULL,
  PRIMARY KEY (`purchase_id`),
  INDEX `fk_purchase_group_goods1_idx` (`group_goods_id` ASC) VISIBLE,
  INDEX `fk_purchase_planning_group1_idx` (`planning_group_pl_gr_id` ASC) VISIBLE,
  CONSTRAINT `fk_purchase_group_goods1`
    FOREIGN KEY (`group_goods_id`)
    REFERENCES `moneykeeper`.`group_goods` (`group_goods_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_purchase_planning_group1`
    FOREIGN KEY (`planning_group_pl_gr_id`)
    REFERENCES `moneykeeper`.`planning_group` (`pl_gr_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `moneykeeper`.`planning_parameter`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `moneykeeper`.`planning_parameter` (
  `pp_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `pp_val` DOUBLE UNSIGNED NOT NULL,
  `date_from` DATE NOT NULL,
  `date_to` DATE NOT NULL,
  `user_id` TINYINT(3) UNSIGNED NOT NULL,
  `planning_date` DATE NULL,
  `planning_last_upd` DATE NULL,
  `purchase_id` INT NOT NULL,
  PRIMARY KEY (`pp_id`),
  INDEX `fk_revenue_user1_idx` (`user_id` ASC) VISIBLE,
  INDEX `fk_planning_parameter_purchase1_idx` (`purchase_id` ASC) VISIBLE,
  CONSTRAINT `fk_revenue_user1`
    FOREIGN KEY (`user_id`)
    REFERENCES `moneykeeper`.`user` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_planning_parameter_purchase1`
    FOREIGN KEY (`purchase_id`)
    REFERENCES `moneykeeper`.`purchase` (`purchase_id`)
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

USE `moneykeeper` ;

-- -----------------------------------------------------
-- procedure upd_plan
-- -----------------------------------------------------

DELIMITER $$
USE `moneykeeper`$$
CREATE PROCEDURE upd_plan(pur_id INTEGER, new_val DOUBLE)

BEGIN
	SELECT pp_val FROM purchase WHERE purchase_id = pur_id;
END;$$

DELIMITER ;

-- -----------------------------------------------------
-- procedure edit_planning_parameter
-- -----------------------------------------------------

DELIMITER $$
USE `moneykeeper`$$
CREATE PROCEDURE `edit_planning_parameter`(p_val DOUBLE, p_d_from DATE, pur INTEGER,
										pl_date DATE, usr INTEGER)
BEGIN
    DECLARE last_val DOUBLE;
    DECLARE last_date_to, last_date_from DATE;
    DECLARE last_pp_id INTEGER;
    
    # Выбор последней даты и значения по purchase_id
	SELECT pp_val, date_from, date_to, pp_id 
    INTO last_val, last_date_from, last_date_to, last_pp_id
    FROM planning_parameter 
	WHERE purchase_id = pur ORDER BY date_to DESC LIMIT 1;
    
    IF last_val IS NULL
	THEN
		# Если запись новая - проверить запись в таблице и добавить
		BEGIN
			DECLARE new_p_id INTEGER;		
			SELECT purchase_id INTO new_p_id FROM purchase WHERE purchase_id = pur;
            IF new_p_id IS NOT NULL
            THEN
				CALL append_new_planpar(pur, p_d_from, p_val, pl_date, usr, DATE_ADD(p_d_from, INTERVAL 1 MONTH));
			END IF;
		END;
	ELSE
		# Если запись уже сущесвтует
		BEGIN
			DECLARE prev_last_date_to DATE;
            SET prev_last_date_to = DATE_SUB(last_date_to, INTERVAL 1 MONTH);
			CASE
				# Запись устаревшая - добавить новую
				WHEN last_date_to <= p_d_from AND last_val <> p_val THEN
					CALL append_new_planpar(pur, last_date_to, p_val, pl_date, usr, DATE_ADD(p_d_from, INTERVAL 1 MONTH));
				# Запись устаревшая, но значение такое же - обновить дату в таблице
                WHEN last_date_to <= p_d_from AND last_val = p_val THEN
					UPDATE planning_parameter
                    SET date_to = DATE_ADD(p_d_from, INTERVAL 1 MONTH)
                    WHERE pp_id = last_pp_id;
				# Если последняя запись от предыдущего месяца - обновить таблицу и добавить строку
				WHEN prev_last_date_to = p_d_from AND last_val <> p_val THEN
					# Если запись спланирована более чем на месяц
					IF prev_last_date_to <> last_date_from THEN
						UPDATE planning_parameter
						SET date_to = prev_last_date_to
						WHERE pp_id = last_pp_id;
                        CALL append_new_planpar(pur, prev_last_date_to, p_val, pl_date, usr, DATE_ADD(p_d_from, INTERVAL 1 MONTH));
					# Если записи всего месяц
                    ELSE
						UPDATE planning_parameter
                        SET pp_val = p_val
                        WHERE pp_id = last_pp_id;
					END IF;
            END CASE;
		END;
	END IF;
END$$

DELIMITER ;

-- -----------------------------------------------------
-- procedure append_new_planpar
-- -----------------------------------------------------

DELIMITER $$
USE `moneykeeper`$$
CREATE PROCEDURE append_new_planpar(pur INTEGER, d_from DATE, 
									p_val DOUBLE, pl_date DATE, usr INTEGER, p_d_to DATE)
BEGIN
	INSERT INTO planning_parameter (pp_val, date_from, date_to, user_id, planning_date, purchase_id)
	VALUES (p_val, d_from, p_d_to, usr, pl_date, pur);
END;$$

DELIMITER ;
USE `moneykeeper`;

DELIMITER $$
USE `moneykeeper`$$
CREATE DEFINER = CURRENT_USER TRIGGER `moneykeeper`.`add_upd_plan_date` BEFORE UPDATE ON `planning_parameter` FOR EACH ROW
BEGIN
	IF NEW.pp_val <> OLD.pp_val THEN
		SET NEW.planning_last_upd = curdate();
    END IF;
END;$$


DELIMITER ;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
