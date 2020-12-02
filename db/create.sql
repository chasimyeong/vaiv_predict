CREATE TABLE log (
    log_state varchar,
    content text,
    date timestamp);

CREATE TABLE input_data (
    input_id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    input_images bytea,
    input_parameters text,
    input_date timestamp);

