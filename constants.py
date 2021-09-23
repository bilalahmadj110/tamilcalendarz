# DATEBASE
SERVER_HOST = 'localhost'
USERNAME = 'root'
PASSWORD = ''
DATABASE = 'tamilcalendar'

TABLE_DATES = 'dates'

TABLE_DATE_INFO = 'date_info'


TABLE_KURAL = 'kural'


TABLE_TAMIL_MONTH = 'tamil_month'


TABLE_DAILY_PALAN = 'daily_palan'
'''
CREATE TABLE `dates`(
    `ID` INT NOT NULL AUTO_INCREMENT,
    `pday` INT NULL DEFAULT NULL,
    `ptamil_month` TINYTEXT NULL,
    `ptamil_star` TINYTEXT NULL,
    `pthithi_name` TINYTEXT NULL,
    `pthithi_img` TINYTEXT NULL,
    `special_day` TINYTEXT NULL,
    `special_img` TINYTEXT NULL,
    `pdata_det` TEXT NULL,
    UNIQUE `ID`(`ID`)
) ENGINE = INNODB CHARSET = utf8mb4 COLLATE utf8mb4_general_ci;

CREATE TABLE `date_info`(
    `ID` INT NOT NULL AUTO_INCREMENT,
    `date_id` INT NOT NULL,
    `date` INT NULL,
    `month` INT NULL,
    `year` INT NULL,
    `today_details` TEXT NULL,
    FOREIGN KEY(`date_id`) REFERENCES dates(`ID`),
    UNIQUE `ID`(`ID`)
) ENGINE = INNODB CHARSET = utf8mb4 COLLATE utf8mb4_general_ci;

CREATE TABLE `kural`(
    `ID` INT NOT NULL AUTO_INCREMENT,
    `date_id` INT NOT NULL,
    `kural` TEXT NULL,
    `pural` TEXT NULL,
    `couplet` TEXT NULL,
    `transliteration` TEXT NULL,
    `explanation` TEXT NULL,
    FOREIGN KEY(`date_id`) REFERENCES dates(`ID`),
    UNIQUE `ID`(`ID`)
) ENGINE = INNODB CHARSET = utf8mb4 COLLATE utf8mb4_general_ci;

CREATE TABLE `tamil_month`(
    `ID` INT NOT NULL AUTO_INCREMENT,
    `date_id` INT NOT NULL,
    `kali` TEXT NULL,
    `year` TEXT NULL,
    `month` TEXT NULL,
    `date` TEXT NULL,
    `eng_month` TEXT NULL,
    `eng_day` TEXT NULL,
    `muslim_year` TEXT NULL,
    `muslim_date` TEXT NULL,
    `muslim_nal` TEXT NULL,
    `muslim_nal_img` TEXT NULL,
    FOREIGN KEY(`date_id`) REFERENCES dates(`ID`),
    UNIQUE `ID`(`ID`)
) ENGINE = INNODB CHARSET = utf8mb4 COLLATE utf8mb4_general_ci;


CREATE TABLE `daily_palan` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `date_id` INT NOT NULL,
  `star` text DEFAULT NULL,
  `god_name` text DEFAULT NULL,
  `palan` text DEFAULT NULL,
  FOREIGN KEY(`date_id`) REFERENCES dates(`ID`),
  UNIQUE `ID`(`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `footer` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `date_id` INT NOT NULL,
  `sulai` TEXT DEFAULT NULL,
  `pariharam` TEXT DEFAULT NULL,
  `chandrashtam` TEXT DEFAULT NULL,
  `nalla_neram_morning` text DEFAULT NULL,
  `nalla_neram_evening` text DEFAULT NULL,
  `gowri_morning` text DEFAULT NULL,
  `gowri_evening` text DEFAULT NULL,
  `rahu_kal_morning` text DEFAULT NULL,
  `rahu_kal_evening` text DEFAULT NULL,
  `guligai_morning` text DEFAULT NULL,
  `guligai_evening` text DEFAULT NULL,
  `yamagandam_morning` text DEFAULT NULL,
  `yamagandam_evening` text DEFAULT NULL,
  `footer` text DEFAULT NULL,
  FOREIGN KEY(`date_id`) REFERENCES dates(`ID`),
  UNIQUE `ID`(`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
'''


TABLE_FOOTER = 'footer'

CHROMEDRIVER_PATH = r'C:\Users\BILAL AHMAD\Desktop\chromedriver.exe'

MAIN_URL = "https://www.tamilcalendarz.com/tamilcalendar.php"
FRAME_URL = "https://www.tamilcalendarz.com/dailysheet.php?dt={date}&amp;tamildate={tamil_date}&amp;tz=Asia/Kolkata&amp;zone=5.5&amp;lt=13.0833,80.2833"

YEAR_FIELD = '//*[@id="yr"]'
MONTH_DROPDOWN = '//*[@id="Mth"]'
GO_BUTTON = '//*[@id="gt"]'

LOADING_FRAME = '//*[@id="frame"]'

CLICK_CELL = '//*[@id="d{date:02d}{month:02d}"]'
DATE_CELL = '//*[@id="{date:02d}{month:02d}"]'

AD = '//*[@id="clos"]'

POPUP_FRAME = '//*[@id="iFrameId"]'

CLICK_OUTSIDE_FRAME = '//*[@id="fcbx"]'

