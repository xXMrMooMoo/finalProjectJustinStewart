-- Drop non-admin tables if they exist
DROP TABLE IF EXISTS carrier_information_iccid2;
DROP TABLE IF EXISTS carrier_information_iccid1;
DROP TABLE IF EXISTS customer_installation_info;
DROP TABLE IF EXISTS cradlepoint_router_status;
DROP TABLE IF EXISTS cradlepoint_routers;

-- Re-create tables
CREATE TABLE cradlepoint_routers (
    router_id INTEGER NOT NULL,
    cradlepoint_mac_address CHAR(17) PRIMARY KEY, -- Format: XX:XX:XX:XX:XX:XX
    model VARCHAR(20) NOT NULL CHECK (model IN ('E110', 'AER1650')), -- Only E110 or AER1650
    iccid1 VARCHAR(22) UNIQUE NOT NULL CHECK (iccid1 LIKE '8914%' AND LENGTH(iccid1) BETWEEN 16 AND 22), -- ICCID1 starts with 8914
    iccid2 VARCHAR(22) UNIQUE NOT NULL CHECK (iccid2 LIKE '8901%' AND LENGTH(iccid2) BETWEEN 16 AND 22), -- ICCID2 starts with 8901
    CHECK (cradlepoint_mac_address LIKE '00:30:%') -- Validates MAC address starts with 00:30
);

CREATE TABLE cradlepoint_router_status (
    cradlepoint_router_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique router status ID
    cradlepoint_mac_address CHAR(17) NOT NULL, -- References cradlepoint_routers
    online_status CHAR(1) NOT NULL CHECK (online_status IN ('Y', 'N')), -- 'Y' for online, 'N' for offline
    FOREIGN KEY (cradlepoint_mac_address) REFERENCES cradlepoint_routers(cradlepoint_mac_address)
        ON DELETE CASCADE -- Deletes status if router is deleted
);

CREATE TABLE customer_installation_info (
    customer_account_number INTEGER PRIMARY KEY, -- User-inputted account number
    cradlepoint_mac_address CHAR(17) NOT NULL, -- References cradlepoint_routers
    customer_address VARCHAR(255) NOT NULL, -- Customer address
    FOREIGN KEY (cradlepoint_mac_address) REFERENCES cradlepoint_routers(cradlepoint_mac_address)
        ON DELETE CASCADE -- Deletes customer info if router is deleted
);

CREATE TABLE carrier_information_iccid1 (
    sim_id INTEGER PRIMARY KEY AUTOINCREMENT,
    iccid VARCHAR(22) NOT NULL UNIQUE,
    provisioning_status VARCHAR(20) NOT NULL CHECK (provisioning_status IN ('active', 'deactive', 'suspended')),
    FOREIGN KEY (iccid) REFERENCES cradlepoint_routers(iccid1)
        ON DELETE CASCADE -- Deletes SIM info if router is deleted
);

CREATE TABLE carrier_information_iccid2 (
    sim_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Primary key
    iccid VARCHAR(22) NOT NULL UNIQUE CHECK (iccid LIKE '8901%'),
    provisioning_status VARCHAR(20) NOT NULL CHECK (provisioning_status IN ('active', 'deactive', 'suspended')),
    FOREIGN KEY (iccid) REFERENCES cradlepoint_routers(iccid2)
        ON DELETE CASCADE -- Deletes SIM info if router is deleted
);
-- Insert sample data into cradlepoint_routers, this is my real testing lab equipment.
INSERT INTO cradlepoint_routers (router_id, cradlepoint_mac_address, model, iccid1, iccid2)
VALUES
    (4088391, '00:30:44:90:71:AE', 'E110', '89148000009064929534', '89011703274018764466'),
    (4262205, '00:30:44:8E:2E:BC', 'E110', '89148000009064925037', '89011703278660107171'),
    (1513893, '00:30:44:3E:52:0B', 'AER1650', '89148000005431245786', '89011703278392368703');

-- Insert sample data into carrier_information_iccid1
INSERT INTO carrier_information_iccid1 (iccid, provisioning_status)
VALUES
    ('89148000009064929534', 'active'),
    ('89148000009064925037', 'active'),
    ('89148000005431245786', 'deactive');

-- Insert sample data into carrier_information_iccid2
INSERT INTO carrier_information_iccid2 (iccid, provisioning_status)
VALUES
    ('89011703274018764466', 'active'),
    ('89011703278660107171', 'active'),
    ('89011703278392368703', 'deactive');

-- Insert sample data into customer_install_info
INSERT INTO customer_installation_info (customer_account_number, cradlepoint_mac_address, customer_address)
VALUES
    (1001, '00:30:44:90:71:AE', '123 Fake Street, Springfield, USA'),
    (1002, '00:30:44:8E:2E:BC', '456 Imaginary Road, Metropolis, USA'),
    (1003, '00:30:44:3E:52:0B', '789 Fictional Ave, Gotham, USA');