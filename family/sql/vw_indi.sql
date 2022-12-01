--drop view family_vw_indi;

create view family_vw_indi as 
with cte_names as (
	select 
		ir.id,
		ir.tree_id,
		ir.sex,
		pns.id as pns_id,
		pnp.id as pnp_id,
		pnp.npfx,
		pnp.givn,
		pnp.nick,
		pnp.spfx,
		pnp.surn,
		pnp.nsfx,
		pnp._marnm,
		mmr.id as mmr_id,
		mmr._prim as mmr_prim,
		mmr._pari as mmr_pari,
		mmr2.id as mmr2_id,
		mmr2._prin as  mmr2_prin,
		replace(mmf.file, rtrim(mmf.file, replace(mmf.file, '/', '')), '') as file,
		replace(mmf2.file, rtrim(mmf2.file, replace(mmf2.file, '/', '')), '') as file2,
		row_number() over(partition by ir.id order by mmr._prim nulls last) as rn,
		mmr._posi as mmr_posi,
		mmr2._posi as mmr2_posi
	from family_individualrecord ir
	left join family_personalnamestructure pns
		on ir.id = pns.indi_id
	left join family_personalnamepieces pnp
		on pns.piec_id = pnp.id
	left join family_multimedialink mml
		on ir.id = mml.indi_id
	left join family_multimediarecord mmr
		on mml.obje_id = mmr.id
	left join family_multimediarecord mmr2
		on mmr._pari = mmr2._prin
		and mmr._prim = 'Y'
		and mmr.tree_id = mmr2.tree_id
	left join family_multimediafile mmf
		on mmr.id = mmf.obje_id
	left join family_multimediafile mmf2
		on mmr2.id = mmf2.obje_id
)
--select * from cte_names where id = 10;
, cte_files as (
	select
		q1.id,
		q1.tree_id,
		q1.sex,
		q1.pns_id,
		q1.pnp_id,
		q1.givn,
		q1.surn,
		q1._marnm,
		coalesce(q1.mmr2_id, q1.mmr_id) as mmr_id,
		q1.mmr_prim,
		coalesce(q1.file2, q1.file) as file,
		coalesce(q1.mmr2_posi, q1.mmr_posi) as mmr_posi
	from cte_names q1
	where q1.rn = 1
)
--select * from cte_files;
, cte_dates as (
	select
		ir.id,
		ir.sex,
		edb.date as birth_src,
		case 
			when length(edb.date) = 11 then substr(edb.date, 8, 4) || '-' || substr(edb.date, 4, 3) || '-' || substr(edb.date, 1, 2)
			when length(edb.date) = 10 then substr(edb.date, 7, 4) || '-' || substr(edb.date, 3, 3) || '-0' || substr(edb.date, 1, 1)
			else edb.date
		end as birth_date,
		edd.date as death_src,
		case 
			when length(edd.date) = 11 then substr(edd.date, 8, 4) || '-' || substr(edd.date, 4, 3) || '-' || substr(edd.date, 1, 2)
			when length(edd.date) = 10 then substr(edd.date, 7, 4) || '-' || substr(edd.date, 3, 3) || '-0' || substr(edd.date, 1, 1)
			else edd.date
		end as death_date,
		psb.name as birth_place,
		psd.name as death_place,
		row_number() over(partition by ir.id order by iesb.id, iesd.id) as rn
	from family_individualrecord ir
	left join family_individualeventstructure iesb
		on ir.id = iesb.indi_id
		and iesb.tag = 'BIRT'
	left join family_eventdetail edb
		on iesb.deta_id = edb.id
	left join family_individualeventstructure iesd
		on ir.id = iesd.indi_id
		and iesd.tag = 'DEAT'
	left join family_eventdetail edd
		on iesd.deta_id = edd.id
	left join family_placestructure psb
		on edb.plac_id = psb.id
	left join family_placestructure psd
		on edd.plac_id = psd.id
)
--select * from cte_dates;
, cte_age as (
	select
		id,
		sex,
		birth_src,
		death_src,
		replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(birth_date, 'JAN', '01'), 'FEB', '02'), 'MAR', '03'), 'APR', '04'), 'MAY', '05'), 'JUN', '06'), 'JUL', '07'), 'AUG', '08'), 'SEP', '09'), 'OCT', '10'), 'NOV', '11'), 'DEC', '12'), 'г.', ''), 'ABT ', '') as birth_date,
		replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(death_date, 'JAN', '01'), 'FEB', '02'), 'MAR', '03'), 'APR', '04'), 'MAY', '05'), 'JUN', '06'), 'JUL', '07'), 'AUG', '08'), 'SEP', '09'), 'OCT', '10'), 'NOV', '11'), 'DEC', '12'), 'г.', ''), 'ABT ', '') as death_date,
		birth_place,
		death_place
	from cte_dates
	where rn = 1
)
--select * from cte_age;
	select
		q1.id,
		q1.tree_id,
		coalesce(q1.sex, '') as sex,
		q1.pns_id,
		q1.pnp_id,
		coalesce(q1.givn, '') as givn,
		coalesce(q1.surn, '') as surn,
		coalesce(q1._marnm, '') as _marnm,
		coalesce(ages.birth_date, '') as birth_date,
		coalesce(ages.birth_place, '') as birth_place,
		coalesce(ages.death_date, '') as death_date,
		coalesce(ages.death_place, '') as death_place,
		coalesce(case 
			when length(ages.birth_date) = 4 and length(ages.death_date) = 4 then cast(ages.death_date as integer) - cast(ages.birth_date as integer) 
			when length(ages.birth_date) = 4 and length(ages.death_date) = 10 then cast(substr(ages.death_date, 1, 4) as integer) - cast(ages.birth_date as integer) 
			when length(ages.birth_date) = 10 and length(ages.death_date) = 4 then cast(ages.death_date as integer) - cast(substr(ages.birth_date, 1, 4) as integer) 
			when length(ages.birth_date) = 10 and length(ages.death_date) = 10 then cast((JulianDay(death_date) - JulianDay(ages.birth_date))/365.25 as integer)
			when length(ages.birth_date) = 10 and ages.death_date is null then cast(((JulianDay('now')) - JulianDay(ages.birth_date))/365.25 as integer)
			when length(ages.birth_date) = 4 and ages.death_date is null then cast(((JulianDay('now')) - JulianDay(ages.birth_date || '-01-01'))/365.25 as integer)
			else null 
		end, '') as age,
		q1.mmr_id,
		coalesce(q1.mmr_prim, '') as mmr_prim,
		coalesce(q1.file, '') as file,
		coalesce(q1.mmr_posi, '') as mmr_posi
	from cte_files as q1
	join cte_age as ages
		on q1.id = ages.id
	--where q1.id = 10
;