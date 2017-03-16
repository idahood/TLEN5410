drop table if exists ospf;
create table ospf (
    name text primary key not null,
    username text not null,
    password text not null,
    proc_id int not null,
    area_id text,
    area_ints text,
    backbone_ints text
);
