
create table players (
    id integer primary key not null,
    name varchar(255),
    team_id integer not null
);

create table matches (
    id integer primary key autoincrement not null,
    player_id integer not null,
    opposition_id integer not null,
    prediction boolean not null default false,
    points integer not null
);
