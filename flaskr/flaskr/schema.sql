/*this schema consist of a single table called entries. Each
    row in this table has an id, a title, and a text. The id is an
    automatically incrementing integer and a primary key, the other
    two are strings that must not be null.
*/
-- drop database if exists bloodBank;
-- create database bloodBank;
-- use bloodBank;

--normalized up to 3NF
DROP TABLE IF EXISTS doctor;
create table doctor (
    d_id        varchar(9),
    d_fname     varchar(20),
    d_lname     varchar(20),
    
    CONSTRAINT PK_doctor 
        PRIMARY KEY (d_id)
);

DROP TABLE IF EXISTS doctor_take_care_of;
create table doctor_take_care_of (
    doctor_id   varchar(9),
    patient_id  varchar(9),
    
    CONSTRAINT PK_doctor_take_care_if 
        PRIMARY KEY (doctor_id, patient_id),
    CONSTRAINT FK_doctor_id
        FOREIGN KEY (doctor_id) REFERENCES doctor (d_id)
            ON DELETE CASCADE       ON UPDATE CASCADE,
    CONSTRAINT FK_patient_id
        FOREIGN KEY (patient_id) REFERENCES patients (p_id)
            ON DELETE CASCADE       ON UPDATE CASCADE
);

DROP TABLE IF EXISTS assists;
create table assists (
    doctor_id   varchar(9),
    nurse_id    varchar(9),
    
    CONSTRAINT PK_assists 
        PRIMARY KEY (doctor_id, nurse_id),
    CONSTRAINT FK_doctor_id
        FOREIGN KEY (doctor_id) REFERENCES doctor (d_id)
            ON DELETE CASCADE       ON UPDATE CASCADE,
    CONSTRAINT FK_nurse_id
        FOREIGN KEY (nurse_id) REFERENCES nurse (n_id)
            ON DELETE SET NULL      ON UPDATE CASCADE
);

DROP TABLE IF EXISTS patients;
create table patients (
    p_id            varchar(9),
    p_fname         varchar(20),
    p_lname         varchar(20),
    blood_type      varchar(3) not null,
    
    CONSTRAINT PK_patients
        PRIMARY KEY (p_id)
);

DROP TABLE IF EXISTS receives_blood;
create table receives_blood (
    patient_id      varchar(9),
    blood_bank_id   varchar(9),
    received_date   date,
    --blood_type attribute is to ensure that the
    --patient receives the right blood type
    blood_type      varchar(3),
    --in ml
    received_amt    numeric(6, 2) DEFAULT 0,
    pack_cnt        numeric(2, 0) DEFAULT 0,

    CONSTRAINT PK_receives_blood
        PRIMARY KEY (patient_id, blood_bank_id),
    CONSTRAINT FK_patient_id
        FOREIGN KEY (patient_id) REFERENCES patients (p_id)
            ON DELETE CASCADE       ON UPDATE CASCADE,
    CONSTRAINT FK_blood_bank_id
        FOREIGN KEY (blood_bank_id) REFERENCES blood_bank (bb_id)
            ON DELETE CASCADE       ON UPDATE CASCADE,
    CONSTRAINT CHK_receives_blood
        CHECK (received_amt > -1 AND pack_cnt > -1)
);

DROP TABLE IF EXISTS donor;
create table donor (
    d_id            varchar(9),
    d_fname         varchar(20),
    d_lname         varchar(20),
    
    CONSTRAINT PK_donor 
        PRIMARY KEY (d_id)
);

DROP TABLE IF EXISTS has_donor_file;
create table has_donor_file (
    donor_id        varchar(9),
    donor_file_id   varchar(9),

    CONSTRAINT PK_has_donor_file
        PRIMARY KEY (donor_id, donor_file_id),
    CONSTRAINT FK_donor_id
        FOREIGN KEY (donor_id) REFERENCES donor (d_id)
            ON DELETE SET NULL      ON UPDATE CASCADE,
    CONSTRAINT FK_donor_file_id
        FOREIGN KEY (donor_file_id) REFERENCES donor_file (df_id)
            ON DELETE CASCADE       ON UPDATE CASCADE
);

DROP TABLE IF EXISTS donor_file;
create table donor_file (
    df_id               varchar(9),
    donor_fname         varchar(20),
    donor_lname         varchar(20),
    blood_type          varchar(3) not null,
    --can be either healthy or unhealthy
    condition           varchar(9) not null,
    --total milliliter donated, each pack is ~500ml
    blood_amt_donated   numeric(6, 2) DEFAULT 0,
    --number of blood packs donated
    num_times_donate    numeric(2, 0) DEFAULT 0,
    blood_bank_id       varchar(9),
    date_last_donated   date,

    CONSTRAINT PK_donor_file
        PRIMARY KEY (df_id),
    CONSTRAINT PK_blood_bank_id
        FOREIGN KEY (blood_bank_id) REFERENCES blood_bank (bb_id)
            ON DELETE SET NULL      ON UPDATE CASCADE,
    CONSTRAINT CHK_donor_file
        CHECK (blood_amt_donated > -1 AND num_times_donate > -1)
);

DROP TABLE IF EXISTS donates_blood;
create table donates_blood (
    donor_id        varchar(9),
    blood_bank_id   varchar(9),
    donated_date    date,

    CONSTRAINT PK_donates_blood
        PRIMARY KEY (donor_id, blood_bank_id),
    CONSTRAINT FK_donor_id
        FOREIGN KEY (donor_id) REFERENCES donor (d_id)
            ON DELETE CASCADE       ON UPDATE CASCADE,
    CONSTRAINT FK_blood_bank_id
        FOREIGN KEY (blood_bank_id) REFERENCES blood_bank (bb_id)
            ON DELETE CASCADE       ON UPDATE CASCADE
);

DROP TABLE IF EXISTS blood_bank;
create table blood_bank (
    bb_id           varchar(9),
    bb_name         varchar(30) not null unique,
    bb_location     varchar(50) not null unique,

    CONSTRAINT PK_blood_bank
        PRIMARY KEY (bb_id)
);

DROP TABLE IF EXISTS transfer_blood;
create table transfer_blood (
    transferred_from    varchar(9),
    from_blood_bank     varchar(30),
    transferred_to      varchar(9),
    to_blood_bank       varchar(30),
    blood_type          varchar(3),
    --total amount of milliliter donated, each pack ~ 500ml
    blood_amt           numeric(12, 2) DEFAULT 0,
    --number of blood packs transferred
    blood_pack_cnt      numeric(4, 0) DEFAULT 0,
    transfer_date       date,

    CONSTRAINT PK_transfer_blood
        PRIMARY KEY (transferred_to, transferred_from, blood_type),
    CONSTRAINT FK_transferred_to
        FOREIGN KEY (transferred_to) REFERENCES blood_bank (bb_id)
            ON UPDATE CASCADE,
    CONSTRAINT FK_transferred_from
        FOREIGN KEY (transferred_from) REFERENCES blood_bank (bb_id)
            ON UPDATE CASCADE,
    CONSTRAINT CHK_transfer_blood
        CHECK (blood_amt > -1 AND blood_pack_cnt > -1)
);

DROP TABLE IF EXISTS bloods;
create table bloods (
    blood_bank_ref_id   varchar(9),
    b_type              varchar(3),
    --total amount of milliliter stored, each apck ~ 500ml
    blood_amt           numeric(7, 2) DEFAULT 0,
    --blood by packs
    num_available       numeric(5, 0) DEFAULT 0,

    CONSTRAINT PK_bloods
        PRIMARY KEY (blood_bank_ref_id, b_type),
    CONSTRAINT CHK_bloods
        CHECK (blood_amt > -1 AND num_available > -1)
);

DROP TABLE IF EXISTS has_blood;
create table has_blood (
    blood_bank_id           varchar(9),
    blood_bank_ref_id       varchar(9),

    CONSTRAINT PK_has_blood
        PRIMARY KEY (blood_bank_id, blood_bank_ref_id),
    CONSTRAINT FK_blood_bank_id
        FOREIGN KEY (blood_bank_id) REFERENCES blood_bank (bb_id)
            ON DELETE SET NULL      ON UPDATE CASCADE,
    CONSTRAINT FK_blood_bank_ref_id
        FOREIGN KEY (blood_bank_ref_id) REFERENCES bloods (b_type)
            ON DELETE CASCADE       ON UPDATE CASCADE
);

DROP TABLE IF EXISTS managed_by;
create table managed_by (
    blood_bank_id   varchar(9),
    nurse_id        varchar(9) unique,

    CONSTRAINT PK_managed_by
        PRIMARY KEY (blood_bank_id),
    CONSTRAINT FK_blood_bank_id
        FOREIGN KEY (blood_bank_id) REFERENCES blood_bank (bb_id)
            ON DELETE SET NULL      ON UPDATE CASCADE,
    CONSTRAINT FK_nurse_id
        FOREIGN KEY (nurse_id) REFERENCES nurse (n_id)
            ON DELETE SET NULL      ON UPDATE CASCADE
);

DROP TABLE IF EXISTS nurse;
create table nurse (
    n_id                varchar(9),
    n_fname             varchar(20),
    n_lname             varchar(20),

    CONSTRAINT PK_nurse
        PRIMARY KEY (n_id)
);

DROP TABLE IF EXISTS nurse_take_care_of;
create table nurse_take_care_of (
    nurse_id    varchar(9),
    patient_id  varchar(9),

    CONSTRAINT PK_nurse_take_care_of
        PRIMARY KEY (nurse_id, patient_id),
    CONSTRAINT FK_nurse_id
        FOREIGN KEY (nurse_id) REFERENCES nurse (n_id)
            ON DELETE SET NULL      ON UPDATE CASCADE,
    CONSTRAINT FK_patient_id
        FOREIGN KEY (patient_id) REFERENCES patients (p_id)
            ON DELETE CASCADE       ON UPDATE CASCADE
);

DROP TABLE IF EXISTS supervise;
create table supervise (
    supervisor_id   varchar(9),
    super_fname     varchar(20),
    super_lname     varchar(20),
    supervised_id   varchar(9),
    ised_fname      varchar(20),
    ised_lname      varchar(20),

    CONSTRAINT PK_supervise
        PRIMARY KEY (supervisor_id, supervised_id),
    CONSTRAINT FK_supervisor_id
        FOREIGN KEY (supervisor_id) REFERENCES nurse (n_id)
            ON DELETE SET NULL      ON UPDATE CASCADE,
    CONSTRAINT FK_supervised_id
        FOREIGN KEY (supervised_id) REFERENCES nurse (n_id)
            ON DELETE CASCADE       ON UPDATE CASCADE
);

DROP TABLE IF EXISTS accounts;
create table accounts (
    id          varchar(9),
    usrName     varchar(9),
    psswd       varchar(9),
    userRole    varchar(7),

    CONSTRAINT PK_accounts
        PRIMARY KEY (id)
);

DROP TABLE IF EXISTS notifications;
create table notifications (
    not_id      varchar(9),
    message     varchar(500),
    u_role      varchar(9),
    m_date      date,
    m_time      time,

    CONSTRAINT PK_not_id
        PRIMARY KEY(not_id),

    CONSTRAINT FK_u_role
        FOREIGN KEY(u_role) REFERENCES accounts (userRole)
);


INSERT INTO accounts VALUES
('1', 'admin@example.com', 'Password1', 'admin'),
('2', 'doctor@example.com', 'Password2', 'doctor'),
('3', 'headNurse@example.com', 'Password3', 'head nurse'),
('4', 'nurse@example.com', 'Password4', 'nurse');

INSERT INTO doctor VALUES
('d12345678', 'Robert',     'Doe'),
('d11223344', 'Harry',      'Beaver'),
('d11122233', 'Alden',      'Cockburn'),
('d11112222', 'Tara',       'Cherry'),
('d01234567', 'Jack',       'Pepper'),
('d00112233' ,'Danny',      'Bonar'),
('d00011122', 'Richard',    'Frankenstein'),
('d00001111', 'Will',       'Tickel');

INSERT INTO doctor_take_care_of VALUES
('d11223344', 'p11223344'),     --Dr. Beaver
('d11112222', 'p11112222'),     --Dr. Cherry
('d11112222', 'p22223333'),
('d01234567', 'p12345678'),     --Dr. Pepper
('d01234567', 'p23456789'),
('d01234567', 'p34567890'),
('d00011122', 'p11122233'),     --Dr. Frankenstein
('d00011122', 'p22233344'),
('d00001111', 'p11112222');     --Dr. Tickel

INSERT INTO assists VALUES      --1-to-1 doctor-nurse match
('d12345678', 'n12345678'),
('d11223344', 'n11223344'),
('d11122233', 'n11122233'),
('d11112222', 'n11112222'),
('d01234567', 'n01234567'),
('d00112233' ,'n00112233'),
('d00011122', 'n00011122'),
('d00001111', 'n00001111');

INSERT INTO patients VALUES
('p11223344', 'Regular',    'Joe',          'A+'),
('p11112222', 'Jane',       'Dope',         'A-'),
('p22223333', 'Charlie',    'Kelly',        'B+'),
('p12345678', 'Dennis',     'Reynolds',     'B-'),
('p23456789', 'Mac',        'Donald',       'O+'),
('p34567890', 'Dee',        'Reynolds',     'O-'),
('p11122233', 'Frank',      'Reynolds',     'AB+'),
('p22233344', 'Bill',       'Ponderosa',    'AB-'),
('p00112233', 'Rickety',    'Cricket',      'A+'),
('p00011122', 'Ryan',       'McPoyle',      'A-'),
--haven't received blood
('p00111222', 'Maureen',    'Ponderosa',    'B+'),
('p01112223', 'Margaret',   'McPoyle',      'B-'),
('p11222333', 'Barbara',    'Reynolds',     'O+');

INSERT INTO receives_blood VALUES
('p11223344', 'bb01234567', '2018-01-01', 'A+',  999.98,  2),
('p11112222', 'bb01234567', '2018-02-03', 'A-',  499.99,  1),
('p22223333', 'bb01234567', '2018-03-05', 'B+',  1011.46, 2),

('p12345678', 'bb12345678', '2018-04-07', 'B-',  504.77,  1),
('p23456789', 'bb12345678', '2018-05-09', 'O+',  1009.54, 2),
('p34567890', 'bb12345678', '2018-06-11', 'O-',  498.88,  1),
('p11122233', 'bb12345678', '2018-07-13', 'AB+', 1022.22, 2),

('p22233344', 'bb23456790', '2018-08-15', 'AB-', 503.17,  1),
('p00112233', 'bb23456790', '2018-09-17', 'A+',  1014.62, 2),
('p00011122', 'bb23456790', '2018-10-19', 'A-',  507.31,  1);

INSERT INTO donor VALUES
('do0123456', 'Rick',   'Sanchez'),
('do1234567', 'Jerry',  'Smith'),
('do2345678', 'Summer', 'Smith'),
('do3456789', 'Beth',   'Smith'),
('do4567890', 'Morty',  'Smith'),
('do5678901', 'Stan',   'Marsh'),
('do6789012', 'Kyle',   'Broflovski'),
('do7890123', 'Eric',   'Cartman'),
('do8901234', 'Kenny',  'McCormick'),
('do9012345', 'Token',  'Black'),
('do0011223', 'Ike',    'Broflovski'),
('do0112233', 'Mister', 'Mackey'),
('do1122334', 'Mister', 'Hankey'),
('do1223344', 'Randy',  'Marsh'),
('do2233445', 'Mister', 'Garrison'),
('do2334455', 'Gerald', 'Broflovski'),
('do3344556', 'Butters','Stotch'),
('do3445566', 'Sheila', 'Broflovski'),
('do4455667', 'Liane',  'Cartman'),
('do4556677', 'Shelley','Marsh'),
('do5566778', 'Officer','Barbrady');

INSERT INTO has_donor_file VALUES 
('do0123456', 'df0123456'),
('do1234567', 'df1234567'),
('do2345678', 'df2345678'),
('do3456789', 'df3456789'),
('do4567890', 'df4567890'),
('do5678901', 'df5678901'),
('do6789012', 'df6789012'),
('do7890123', 'df7890123'),
('do8901234', 'df8901234'),
('do9012345', 'df9012345'),
('do0011223', 'df0011223'),
('do0112233', 'df0112233'),
('do1122334', 'df1122334'),
('do1223344', 'df1223344'),
('do2233445', 'df2233445'),
('do2334455', 'df2334455'),
('do3344556', 'df3344556'),
('do3445566', 'df3445566'),
('do4455667', 'df4455667'),
('do4556677', 'df4556677'),
('do5566778', 'df5566778');

/*
possibilities:
--------------
1) healthy person turned unhealthy
2) unhealthy person turned healthy
3) always been unhealthy
4) always been healthy
*/
INSERT INTO donor_file VALUES
('df0123456', 'Rick',   'Sanchez',      'A+', 'healthy', 1000.10, 2, 'bb01234567',      '2018-11-10'),
('df1234567', 'Jerry',  'Smith',        'A-', 'healthy', 1500.11, 3, 'bb01234567',      '2017-11-21'),
('df2345678', 'Summer', 'Smith',        'B+', 'healthy', 2000.12, 4, 'bb01234567',
    '2017-10-19'),
--used to  be healthy
('df3456789', 'Beth',   'Smith',        'B-', 'unhealthy', 500.01, 1,'bb01234567',
    '2017-09-17'),
('df4567890', 'Morty',  'Smith',        'O+', 'healthy', 1000.20, 2, 'bb01234567',
    '2017-08-15'),
('df5678901', 'Stan',   'Marsh',        'O-', 'healthy', 1500.21, 3, 'bb01234567',
    '2017-07-13'),
('df6789012', 'Kyle',   'Broflovski',   'AB+','healthy', 2000.22, 4, 'bb01234567',
    '2017-06-11'),
--have always been unhealthy
('df7890123', 'Eric',   'Cartman',      'AB-','unhealthy', 0, 0, null, null),
('df8901234', 'Kenny',  'McCormick',    'A+', 'healthy', 1000.30, 2, 'bb12345678',
    '2016-05-09'),
('df9012345', 'Token',  'Black',        'A-', 'healthy', 1500.31, 3, 'bb12345678',
    '2016-04-07'),
('df0011223', 'Ike',    'Broflovski',   'B+', 'healthy', 2000.32, 4, 'bb12345678',
    '2016-03-05'),
--used to be healthy
('df0112233', 'Mister', 'Mackey',       'B-', 'unhealthy', 500.02, 1,'bb12345678',
    '2016-02-03'),
('df1122334', 'Mister', 'Hankey',       'O+', 'healthy', 1000.40, 2, 'bb12345678',
    '2016-01-01'),
('df1223344', 'Randy',  'Marsh',        'O-', 'healthy', 1500.41, 3, 'bb12345678',
    '2016-12-28'),
('df2233445', 'Mister', 'Garrison',     'AB+','healthy', 2000.42, 4, 'bb12345678',
    '2016-11-26'),
--have always been unhealthy
('df2334455', 'Gerald', 'Broflovski',   'AB-','unhealthy', 0, 0, null, null),
('df3344556', 'Butters','Stotch',       'A+', 'healthy', 1000.50, 2, 'bb23456790',
    '2015-10-24'),
('df3445566', 'Sheila', 'Broflovski',   'A-', 'healthy', 1500.51, 3, 'bb23456790',
    '2015-09-22'),
('df4455667', 'Liane',  'Cartman',      'B+', 'healthy', 2000.52, 4, 'bb23456790',
    '2015-08-20'),
--used to be healthy
('df4556677', 'Shelley','Marsh',        'B-', 'unhealthy', 500.03, 1,'bb23456790',
    '2015-07-18'),
('df5566778', 'Officer','Barbrady',     'O+', 'healthy', 1000.60, 2, 'bb23456790',
    '2015-06-16');

INSERT INTO donates_blood VALUES
('do0123456', 'bb01234567', '2017-12-23'),
('do1234567', 'bb01234567', '2017-11-21'),
('do2345678', 'bb01234567', '2017-10-19'),

('do3456789', 'bb01234567', '2017-09-17'),
('do4567890', 'bb01234567', '2017-08-15'),
('do5678901', 'bb01234567', '2017-07-13'),
('do6789012', 'bb01234567', '2017-06-11'),

('do8901234', 'bb12345678', '2016-05-09'),
('do9012345', 'bb12345678', '2016-04-07'),
('do0011223', 'bb12345678', '2016-03-05'),

('do0112233', 'bb12345678', '2016-02-03'),
('do1122334', 'bb12345678', '2016-01-01'),
('do1223344', 'bb12345678', '2016-12-28'),
('do2233445', 'bb12345678', '2016-11-26'),

('do3344556', 'bb23456790', '2015-10-24'),
('do3445566', 'bb23456790', '2015-09-22'),
('do4455667', 'bb23456790', '2015-08-20'),

('do4556677', 'bb23456790', '2015-07-18'),
('do5566778', 'bb23456790', '2015-06-16');

INSERT INTO blood_bank VALUES
('bb01234567', 'Hema Care', 'Sesame Street, Penngrove, CA'),
('bb12345678', 'Life Source', 'Jive Turkey Lane, Oroville, CA'),
('bb23456790', 'One Blood', 'Candy Cane Lane, North Cindy Avenue, Clovis, CA');

INSERT INTO transfer_blood VALUES
--from Hema Care to Life Source
('bb12345678', 'Hema Care',     'bb01234567', 'Life Source', 'A+', 151844.00, 300,  '2016-09-27'),
('bb12345678', 'Hema Care',     'bb01234567', 'Life Source', 'B+', 37958.25, 75,    '2016-08-25'),
--from Life Source to Hema Care
('bb01234567', 'Life Source',   'bb12345678', 'Hema Care',   'AB-', 10122.20, 20,   '2016-07-23'),
--from Life Source to One Blood
('bb23456790', 'Life Source',   'bb12345678', 'One Blood',   'AB+', 10118.37, 20,   '2016-06-21'),
--from One Blood to Hema Care
('bb01234567', 'One Blood',     'bb23456790', 'Hema Care',   'O+', 50611.00, 100,   '2016-05-19'),
('bb01234567', 'One Blood',     'bb23456790', 'Hema Care',   'B-', 25305.50, 50,    '2016-04-17');

INSERT INTO bloods VALUES
--5040 pints of blood/ blood bank for 4 months
--Hema Care
('br01234567', 'A+',  957902.15, 1915),
('br01234567', 'A-',  957863.85, 353),
('br01234567', 'B+',  856928.25, 1713),
('br01234567', 'B-',  151075.50, 302),
('br01234567', 'O+',  227095.34, 454),
('br01234567', 'O-',  50521.21,  101),
('br01234567', 'AB+', 75528.69,  151),
('br01234567', 'AB-', 25009.50,  50),
--Life Source
('br12345678', 'A+',  941134.95, 1865),
('br12345678', 'A-',  203365.89, 403),
('br12345678', 'B+',  833794.94 ,1663),
('br12345678', 'B-',  957863.85, 353),
('br12345678', 'O+',  202056.14, 403),
('br12345678', 'O-',  75708.38, 151),
('br12345678', 'AB+', 50639.38,  101),
('br12345678', 'AB-', 50521.21,  101),
--One Blood
('br23456790', 'A+',  958475.70, 1890),
('br23456790', 'A-',  191695.14, 378),
('br23456790', 'B+',  856035.44, 1688),
('br23456790', 'B-',  166338.64, 328),
('br23456790', 'O+',  217051.64, 428),
('br23456790', 'O-',  64405.51,  127),
('br23456790', 'AB+', 63391.25,  125),
('br23456790', 'AB-', 38034.75,  75);

INSERT INTO has_blood VALUES
('bb01234567', 'br01234567'),
('bb12345678', 'br12345678'),
('bb23456790', 'br23456790');

INSERT INTO managed_by VALUES
('bb01234567', 'n11122233'),
('bb12345678', 'n00112233'),
('bb23456790', 'n00011122');

INSERT INTO nurse VALUES
('n12345678', 'Moar', 'Payne'),
('n11223344', 'Annie', 'Beaver'),
('n22334455', 'Tofer', 'Splean'),     --no use
--head nurse
('n11122233', 'Sophie', 'Hacker'),
('n11112222', 'Lorry', 'Cox'),
('n01234567', 'Jenny', 'Fang'),
('n90123456', 'Cathy', 'Kity'),       --no use
--head nurse
('n00112233' ,'Mary', 'Slaughter'),
--head nurse
('n00011122', 'Melika', 'Kutsche'),
('n00001111', 'Will', 'Scarry'),
('n99990000', 'Dorothea', 'Dix');       --no use

INSERT INTO nurse_take_care_of VALUES
('n12345678', 'p11112222'),     --Nurse Payne
('n12345678', 'p22223333'),
('n11223344', 'p11223344'),     --Nurse Beaver
('n11122233', 'p11223344'),     --Nurse Hacker
('n11223344', 'p00112233'),
('n11112222', 'p11112222'),     --Nurse Cox
('n01234567', 'p11112222'),     --Nurse Fang
('n00112233', 'p11122233'),     --Nurse Slaughter
('n00112233', 'p22233344'),
('n00011122', 'p00011122'),     --Nurse Kutsche
('n00001111', 'p12345678'),     --Nurse Scarry
('n00001111', 'p23456789'),
('n00001111', 'p34567890');

-- supervisor_id   varchar(9),
-- super_fname     varchar(20),
-- super_lname     varchar(20),
-- supervised_id   varchar(9),
-- ised_fname      varchar(20),
-- ised_lname      varchar(20),

INSERT INTO supervise VALUES
--Hacker to Payne
('n11122233', 'Sophie', 'Hacker', 'n12345678', 'Moar', 'Payne'),   
--Hacker to Beaver
('n11122233', 'Sophie', 'Hacker', 'n11223344', 'Annie', 'Beaver'),
--Kutsche to Splean
('n00011122', 'Melika', 'Kutsche','n22334455', 'Tofer', 'Splean'),
--Slaughter to Cox
('n00112233', 'Mary', 'Slaughter','n11112222', 'Lorry', 'Cox'),
--Slaughter to Fang
('n00112233', 'Mary', 'Slaughter', 'n01234567', 'Jenny', 'Fang'),
--Hacker to Kity
('n11122233', 'Sophie', 'Hacker', 'n90123456', 'Cathy', 'Kitty'),  --Kutsche to Scarry
('n00011122', 'Melika', 'Kutsche', 'n00001111', 'Will', 'Scarry'),
--Slaughter to Dix
('n00112233', 'Mary', 'Slaughter', 'n99990000', 'Dorothea', 'Dix');