DROP PROCEDURE IF EXISTS get_cap_range;

DELIMITER $$ 

CREATE PROCEDURE get_cap_range(
    IN  option_str  VARCHAR(255),
    out lower_bound FLOAT,
    out upper_bound FLOAT
) 
BEGIN
    CASE option_str
        WHEN 'Micro(<$300mln)' THEN
            SELECT min(market_cap) 
            INTO lower_bound
            FROM screening;
            SET upper_bound = 3e8;
        WHEN 'Small($300mln~$2bln)' THEN
            SET lower_bound = 3e8;
            SET upper_bound = 2e9;
        WHEN 'Mid($2bln~$10bln)' THEN
            SET lower_bound = 2e9;
            SET upper_bound = 1e10;
        WHEN 'Large(>$10bln)' THEN
            SET lower_bound =1e10;
            SELECT MAX(market_cap)
            INTO upper_bound
            FROM screening;
        ELSE
            SELECT MIN(market_cap), max(market_cap) 
            INTO lower_bound, upper_bound
            FROM screening;
    END CASE;

END $$ 

DELIMITER ;


DROP PROCEDURE IF EXISTS get_sma_range;

DELIMITER $$ 

CREATE PROCEDURE get_sma_range(
    IN  option_str  VARCHAR(255),
    out lower_bound FLOAT,
    out upper_bound FLOAT
) 
BEGIN
    CASE option_str
        WHEN 'Price above SMA200' THEN
            SELECT max(sma200)
            INTO upper_bound
            FROM screening;
            SET lower_bound = 0;
        WHEN 'Price below SMA200' THEN
            SELECT min(sma200)
            INTO lower_bound
            FROM screening;
            SET upper_bound = 0;
        ELSE
            SELECT MIN(sma200), max(sma200) 
            INTO lower_bound, upper_bound
            FROM screening;
    END CASE;

END $$ 

DELIMITER ;


DROP PROCEDURE IF EXISTS get_ps_range;

DELIMITER $$ 

CREATE PROCEDURE get_ps_range(
    IN  option_str  VARCHAR(255),
    out lower_bound FLOAT,
    out upper_bound FLOAT
) 
BEGIN
    CASE option_str
        WHEN 'High(>10)' THEN
            SELECT max(price_to_sales)
            INTO upper_bound
            FROM screening;
            SET lower_bound = 10;
        WHEN 'Low(<1)' THEN
            SELECT min(price_to_sales)
            INTO lower_bound
            FROM screening;
            SET upper_bound = 1;
        WHEN 'Under 10' THEN
            SELECT min(price_to_sales)
            INTO lower_bound
            FROM screening;
            SET upper_bound = 10;
        ELSE
            SELECT MIN(price_to_sales), max(price_to_sales) 
            INTO lower_bound, upper_bound
            FROM screening;
    END CASE;

END $$ 

DELIMITER ;


DROP PROCEDURE IF EXISTS get_gm_range;

DELIMITER $$ 

CREATE PROCEDURE get_gm_range(
    IN  option_str  VARCHAR(255),
    out lower_bound FLOAT,
    out upper_bound FLOAT
) 
BEGIN
    CASE option_str
        WHEN 'Positive(>0%)' THEN
            SELECT max(gross_margin)
            INTO upper_bound
            FROM screening;
            SET lower_bound = 0;
        WHEN 'Negative(<0%)' THEN
            SELECT min(gross_margin)
            INTO lower_bound
            FROM screening;
            SET upper_bound = 0;
        WHEN 'High(>50%)' THEN
            SELECT max(gross_margin)
            INTO upper_bound
            FROM screening;
            SET lower_bound = 0.5;
        ELSE
            SELECT MIN(gross_margin), max(gross_margin) 
            INTO lower_bound, upper_bound
            FROM screening;
    END CASE;

END $$ 

DELIMITER ;


DROP PROCEDURE IF EXISTS get_pm_range;

DELIMITER $$ 

CREATE PROCEDURE get_pm_range(
    IN  option_str  VARCHAR(255),
    out lower_bound FLOAT,
    out upper_bound FLOAT
) 
BEGIN
    CASE option_str
        WHEN 'Positive(>0%)' THEN
            SELECT max(profit_margin)
            INTO upper_bound
            FROM statistics;
            SET lower_bound = 0;
        WHEN 'Negative(<0%)' THEN
            SELECT min(profit_margin)
            INTO lower_bound
            FROM statistics;
            SET upper_bound = 0;
        WHEN 'High(>20%)' THEN
            SELECT max(profit_margin)
            INTO upper_bound
            FROM statistics;
            SET lower_bound = 0.2;
        ELSE
            SELECT MIN(profit_margin), max(profit_margin) 
            INTO lower_bound, upper_bound
            FROM statistics;
    END CASE;

END $$ 

DELIMITER ;


DROP PROCEDURE IF EXISTS get_om_range;

DELIMITER $$ 

CREATE PROCEDURE get_om_range(
    IN  option_str  VARCHAR(255),
    out lower_bound FLOAT,
    out upper_bound FLOAT
) 
BEGIN
    CASE option_str
        WHEN 'Positive(>0%)' THEN
            SELECT max(operating_margin)
            INTO upper_bound
            FROM statistics;
            SET lower_bound = 0;
        WHEN 'Negative(<0%)' THEN
            SELECT min(operating_margin)
            INTO lower_bound
            FROM statistics;
            SET upper_bound = 0;
        WHEN 'High(>25%)' THEN
            SELECT max(operating_margin)
            INTO upper_bound
            FROM statistics;
            SET lower_bound = 0.25;
        WHEN 'Very Negative(<-20%)' THEN
            SELECT min(operating_margin)
            INTO lower_bound
            FROM statistics;
            SET upper_bound = -0.2;
        ELSE
            SELECT MIN(operating_margin), max(operating_margin) 
            INTO lower_bound, upper_bound
            FROM statistics;
    END CASE;

END $$ 
DELIMITER ;



DROP PROCEDURE IF EXISTS filter_stocks;

DELIMITER $$

CREATE PROCEDURE filter_stocks(
    IN str_cap VARCHAR(255),
    IN str_sma VARCHAR(255),
    IN str_ps VARCHAR(255),
    IN str_gm VARCHAR(255),
    IN str_pm VARCHAR(255),
    IN str_om VARCHAR(255)
) 
BEGIN
    DECLARE
        min_cap, max_cap,
        min_sma, max_sma,
        min_ps, max_ps,
        min_gm, max_gm,
        min_pm, max_pm,
        min_om, max_om FLOAT DEFAULT 0.0;

    CALL get_cap_range(str_cap, @min_cap, @max_cap);
    CALL get_sma_range(str_sma, @min_sma, @max_sma);
    CALL get_ps_range(str_ps, @min_ps, @max_ps);
    CALL get_gm_range(str_gm, @min_gm, @max_gm);
    CALL get_pm_range(str_pm, @min_pm, @max_pm);
    CALL get_om_range(str_om, @min_om, @max_om);

    SELECT t1.symbol, market_cap, sma200, price_to_sales, 
           gross_margin, t2.profit_margin, t2.operating_margin
    FROM
    (SELECT * 
    FROM screening
    WHERE market_cap BETWEEN @min_cap AND @max_cap
    AND sma200 BETWEEN @min_sma AND @max_sma
    AND price_to_sales BETWEEN @min_ps AND @max_ps
    AND gross_margin BETWEEN @min_gm AND @max_gm) AS t1
    INNER JOIN
    (SELECT symbol, profit_margin, operating_margin 
    FROM statistics
    WHERE profit_margin BETWEEN @min_pm AND @max_pm
    AND operating_margin BETWEEN @min_om AND @max_om) AS t2
    ON t1.symbol = t2.symbol;

END $$ 

DELIMITER ;


