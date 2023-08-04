create table log_date (
    id integer primary key autoincrement,
    entry_day date not null
);

create table food (
    id integer primary key autoincrement,
    name text not null,
    protein text not null,
    carbohydrates text not null,
    fat text not null,
    calories text not null
);

create table food_date (
    food_id integer not null,
    log_date_id integer not null,
    primary key(food_id, log_date_id)

);