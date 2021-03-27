
create table players (
    id integer primary key not null,
    first_name varchar(255),
    surname varchar(255),
    team_id integer not null,
    current_cost real not null,
    position integer not null
);

create table matches (
    id integer primary key autoincrement not null,
    player_id integer not null,
    minutes real not null,
    points real not null,
    gameweek integer not null
);

create table future_matches (
    id integer primary key autoincrement not null,
    player_id integer not null,
    minutes real not null,
    points real not null,
    gameweek integer not null
);
