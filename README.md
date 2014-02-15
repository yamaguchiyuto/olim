OLIM
---

# Usage

Output lines of error distances.

```bash
> python olim.py [training] [test | validate] [params] [db user] [db pass] [db name] [model] > result

> head -n5 result
654793.062001	<- Error distance (m) of a user
119541.481423
29103.1556068
262796.132273
114966.398399

> python summary.py result
27024.647569 	<- Median ED (m)
0.639160		<- Precision
```

# Parameters

## `params.json`

```bash
> cat data/params.json
{"dmin": 1.0, "N": 400, "lang": "ja", "K": 100}
```

# Data

##Users

### `users.json`
Users in the dataset used in the paper.
All users in this file are labeled users.

```bash
> wc data/users.json
 201570 1007850 9944922 users.json

> head -n20 data/users.json
{"location": [34.6813, 135.51], "id": 15204353}
{"location": [35.6581, 139.752], "id": 215657131}
{"location": [33.8809, 130.873], "id": 91226119}
{"location": [34.4859, 132.362], "id": 167772168}
{"location": [35.6581, 139.752], "id": 135790601}
{"location": [35.5297, 139.704], "id": 116916234}
{"location": [34.9877, 135.756], "id": 486539277}
{"location": [35.6947, 139.983], "id": 55574543}
{"location": [35.4447, 139.642], "id": 73400336}
{"location": [35.1687, 136.91], "id": 106430481}
{"location": [36.5551, 139.883], "id": 128974868}
{"location": [35.6581, 139.752], "id": 9437212}
{"location": [34.6951, 135.198], "id": 196608029}
{"location": [32.7503, 129.878], "id": 89653278}
{"location": [35.6878, 139.775], "id": 60293152}
{"location": [34.6813, 135.51], "id": 116391970}
{"location": [31.5966, 130.557], "id": 82313251}
{"location": [35.6581, 139.752], "id": 332398629}
{"location": [35.7757, 139.804], "id": 134742054}
{"location": [35.6947, 139.983], "id": 165675048}
```
### `training.90.json`

Users in the training set are the same as those in `users.json`, but loactions of 10% of them are masked.

```bash
> wc data/training.90.json
 201570  988304 9675812 training.90.json

> head -n20 data/training.90.json
{"location": [34.6813, 135.51], "id": 15204353}
{"location": [35.6581, 139.752], "id": 215657131}
{"location": [33.8809, 130.873], "id": 91226119}
{"location": [34.4859, 132.362], "id": 167772168}
{"location": [35.6581, 139.752], "id": 135790601}
{"location": [35.5297, 139.704], "id": 116916234}
{"location": [34.9877, 135.756], "id": 486539277}
{"location": [35.6947, 139.983], "id": 55574543}
{"location": [35.4447, 139.642], "id": 73400336}
{"location": [35.1687, 136.91], "id": 106430481}
{"location": [36.5551, 139.883], "id": 128974868}
{"location": [35.6581, 139.752], "id": 9437212}
{"location": [34.6951, 135.198], "id": 196608029}
{"location": [32.7503, 129.878], "id": 89653278}
{"location": [35.6878, 139.775], "id": 60293152}
{"location": null, "id": 116391970}
{"location": [31.5966, 130.557], "id": 82313251}
{"location": [35.6581, 139.752], "id": 332398629}
{"location": [35.7757, 139.804], "id": 134742054}
{"location": [35.6947, 139.983], "id": 165675048}
```

### `test.5.json`

5% of all users, which are masked in `training.90.json`.

```bash
> wc data/test.5.json
 9686  48430 478471 test.5.json
> head -n5 data/test.5.json
{"location": [34.6813, 135.51], "id": 116391970}
{"location": [35.664, 139.698], "id": 60817470}
{"location": [35.0104, 135.751], "id": 113246290}
{"location": [34.6951, 135.198], "id": 92274950}
{"location": [36.5551, 139.883], "id": 150995210}
```
### `validate.5.json`

5% of all users, which are masked in `training.90.json`.
Users in this file are different from those in `test.5.json`.

```bash
> wc data/validate.5.json
 9860  49300 486991 validate.5.json

> head -n5 data/validate.5.json
{"location": [35.662, 139.699], "id": 211462840}
{"location": [35.0608, 136.125], "id": 470286440}
{"location": [34.6813, 135.51], "id": 18350220}
{"location": [34.6813, 135.51], "id": 151519380}
{"location": [39.72, 140.103], "id": 183500840}
```

## Graph

### `graph.json`

Follow relationships among all users in `users.json`.

```bash
> wc data/graph.json
 201570  34214067 361562939 graph.json

> head -n2 data/graph.json
{"src_id": 15204353, "dst_ids": [3874831, …, 620772247]}
{"src_id": 215657131, "dst_ids": [9995652, …, 211604661]}
```

## Tweet

Unfortunatelly, Twitter does not allow us to share the data of tweets. So we suggest you to collect the latest 200 tweets of users in `users.json`.

Prepare the tweet data as the following scheme.

```sql
mysql (none) > use dbname

mysql dbname > show tables;
+---------------------+
|  Tables_in_dbname   |
+---------------------+
| tweets              |
+---------------------+
1 rows in set (0.00 sec)

mysql dbname > show fields from tweets;
+-----------+------------+------+-----+---------+-------+
| Field     | Type       | Null | Key | Default | Extra |
+-----------+------------+------+-----+---------+-------+
| id        | bigint(20) | NO   | PRI | 0       |       |
| text      | text       | YES  |     | NULL    |       |
| timestamp | datetime   | YES  | MUL | NULL    |       |
| user_id   | bigint(20) | YES  | MUL | NULL    |       |
+-----------+------------+------+-----+---------+-------+
4 rows in set (0.00 sec)	
```
