# Weather trajectory and forecast revisions: exploratory follow-ups

The completed portfolio release is preserved. These are two additional, bounded experiments in the same NYC electricity project, not stock trading. Both predict hour-18 real-time minus day-ahead prices at 04:00 ET on the prior day. Positive forecast means virtual load; negative means virtual supply. All dollars assume one MWh clears per signal, before fees, uplift, slippage and financing.

**Both 2024 and 2025 were examined in earlier work. These are exploratory results, not fresh confirmation of alpha.** The two related hypothesis comparisons are not corrected for multiple testing. No variant was promoted based on its 2025 score.

## Main finding
Neither follow-up establishes reliable incremental gross alpha. The selected forecast trajectory earned $1,121.88 versus $776.12 for its matched linear baseline; its increment remains uncertain. Forecast revisions earned $982.62 versus $1,020.96 for the matched linear baseline. Both remain dominated by the June 24 extreme-price day. Trajectory uses 356 dates; revision uses 362. Do not rank their raw totals across cohorts.

## What changed

**Trajectory:** add the difference between forecast evening temperatures for D and D−1, optionally also D−2, to the existing linear-weather/calendar model. These are forecasts issued on different dates. They are not realized temperature lags or evidence that stock prices react slowly. At the decision cutoff, D−1 evening has not yet occurred. The proxy can mix weather evolution with forecast errors.

**Revisions:** add the six-hour change between 00 UTC and 06 UTC forecasts for the SAME next-day evening temperature at the SAME grid point. Both must be archived before the cutoff buffer. Leads are 46/47 versus 40/41 hours. Thus this compares changes in forecast expectations rather than changes in the weather target date.

Development fit 2021–2023, selection 2024, refit 2021–2024, evaluate 2025. Trajectory variant selection uses validation gross payoff; revision has one fixed variant. Calendar/linear baselines are refitted on each family's exact eligible cohort. Cross-family dollar totals are not a fair ranking because cohorts differ.

## Trajectory result

Selected variant: **1-day trajectory**. Eligible evaluation dates: **356**.

- Selected gross payoff: **$1,121.88**.
- Same-cohort original linear: **$776.12**; always virtual load: **$609.06**.
- Increment over linear: **$0.97/decision**, seven-day 95% interval **[$-0.16, $2.61]**.
- Increment over always-load: **$1.44/decision**, interval **[$-5.27, $7.92]**.
- Raw gross mean versus flat interval: **[$-6.23, $16.46]**.
- Best day **2025-06-24**, payoff **$1,768.53**; remaining dates **$-646.65**. Positive months: **4 of 12**.

**Interpretation:** This comparison does not establish reliable incremental gross alpha over the original linear model and constant-direction benchmark.

### Validation selection and all alternatives


```csv
strategy,days,active_trades,virtual_load_days,virtual_supply_days,flat_days,total_gross_dollars,mean_daily_gross_dollars,mean_active_trade_dollars,win_rate_active,zero_payoff_active_trades,daily_std_dollars,best_day_dollars,worst_day_dollars,fifth_percentile_dollars,worst_five_percent_mean_dollars,max_drawdown_dollars
calendar,360,360,201,159,0,1672.5199999999995,4.645888888888887,4.645888888888887,0.4944444444444444,0,63.58783917206637,828.7299999999999,-132.61,-42.943000000000005,-72.8488888888889,621.4700000000007
linear,360,360,202,158,0,1589.9599999999996,4.416555555555554,4.416555555555554,0.4916666666666666,0,63.60422470527428,828.7299999999999,-132.61,-43.120000000000005,-73.41333333333333,625.3100000000004
trajectory1,360,360,202,158,0,1591.0399999999995,4.419555555555554,4.419555555555554,0.4805555555555555,0,63.60401573946663,828.7299999999999,-132.61,-42.592,-72.71222222222222,680.4500000000007
trajectory2,360,360,201,159,0,1461.2199999999996,4.058944444444443,4.058944444444443,0.4611111111111111,0,63.62811309508928,828.7299999999999,-132.61,-42.592,-72.36277777777778,725.4100000000003
always_load,360,360,360,0,0,568.2599999999998,1.5784999999999991,1.5784999999999991,0.3583333333333333,0,63.73820749503131,828.7299999999999,-130.73000000000002,-45.2805,-67.22611111111111,952.76
always_supply,360,360,0,360,0,-568.2599999999998,-1.5784999999999991,-1.5784999999999991,0.6416666666666667,0,63.73820749503131,130.73000000000002,-828.7299999999999,-50.401500000000006,-173.88444444444443,1827.3199999999997
flat,360,0,0,0,360,0.0,0.0,,,0,0.0,0.0,-0.0,0.0,0.0,0.0
training_mean,360,360,360,0,0,568.2599999999998,1.5784999999999991,1.5784999999999991,0.3583333333333333,0,63.73820749503131,828.7299999999999,-130.73000000000002,-45.2805,-67.22611111111111,952.76
```

### Final strategy metrics (including unselected alternatives)

```csv
group_type,group,strategy,days,active_trades,virtual_load_days,virtual_supply_days,flat_days,total_gross_dollars,mean_daily_gross_dollars,mean_active_trade_dollars,win_rate_active,zero_payoff_active_trades,daily_std_dollars,best_day_dollars,worst_day_dollars,fifth_percentile_dollars,worst_five_percent_mean_dollars,max_drawdown_dollars,spread_mae_mwh,spread_rmse_mwh
overall,all,calendar,356,356,192,164,0,-115.09999999999992,-0.3233146067415727,-0.3233146067415727,0.4213483146067415,0,110.30796265729032,1768.5300000000002,-302.82,-95.2875,-146.46777777777777,1382.41,35.60223767286289,109.69495482801032
overall,all,linear,356,356,195,161,0,776.1200000000006,2.1801123595505634,2.1801123595505634,0.4410112359550562,0,110.28683137198136,1768.5300000000002,-233.7,-78.6425,-134.82555555555555,943.1999999999996,35.389436808405854,109.39377950837576
overall,all,trajectory1,356,356,199,157,0,1121.8800000000003,3.1513483146067425,3.1513483146067425,0.4522471910112359,0,110.26328709755214,1768.5300000000002,-233.7,-71.43750000000001,-132.54722222222222,943.1999999999994,35.287785203583965,109.39076902170956
overall,all,trajectory2,356,356,190,166,0,1180.7000000000005,3.316573033707866,3.316573033707866,0.4662921348314606,0,110.25842739109802,1768.5300000000002,-233.7,-78.6425,-134.82555555555555,943.1999999999994,35.24938990139039,109.31741205642382
overall,all,always_load,356,356,356,0,0,609.0600000000002,1.710842696629214,1.710842696629214,0.3258426966292135,0,110.29513237056284,1768.5300000000002,-233.7,-54.9375,-115.28222222222225,1384.6799999999996,,
overall,all,always_supply,356,356,0,356,0,-609.0600000000002,-1.710842696629214,-1.710842696629214,0.6741573033707865,0,110.29513237056284,233.7,-1768.5300000000002,-78.30749999999999,-266.5755555555556,2147.3500000000004,,
overall,all,flat,356,0,0,0,356,0.0,0.0,,,0,0.0,0.0,-0.0,-0.0,0.0,0.0,,
overall,all,training_mean,356,356,356,0,0,609.0600000000002,1.710842696629214,1.710842696629214,0.3258426966292135,0,110.29513237056284,1768.5300000000002,-233.7,-54.9375,-115.28222222222225,1384.6799999999996,,
```

### All block-length sensitivity intervals

```csv
selected,benchmark,block_days,mean_increment,lower_95,upper_95
trajectory1,linear,7,0.9712359550561798,-0.1611582559982763,2.608646159356399
trajectory1,linear,14,0.9712359550561798,-0.0456409019688529,2.389481737012986
trajectory1,linear,28,0.9712359550561798,-0.059421270718232,2.488363083164298
trajectory1,calendar,7,3.4746629213483144,0.4381184929027787,7.853194765552448
trajectory1,calendar,14,3.4746629213483144,0.6163210609812717,7.693152857829004
trajectory1,calendar,28,3.4746629213483144,0.707906912233183,7.604842378292096
trajectory1,always_load,7,1.4405056179775293,-5.269316488427773,7.921448323760031
trajectory1,always_load,14,1.4405056179775293,-4.988729913039451,7.5902568516068785
trajectory1,always_load,28,1.4405056179775293,-4.4244841046277665,7.313517210208181
trajectory1,flat,7,3.1513483146067434,-6.233035200199188,16.456815028248588
trajectory1,flat,14,3.1513483146067434,-6.473227702315521,17.681308103636134
trajectory1,flat,28,3.1513483146067434,-5.274938096949975,15.780346705456765
```

Data gate: 1780 eligible of 1,826 dates, 46 exclusions. No imputations or actual-future-weather substitution.

## Revision result

Selected variant: **6-hour revision**. Eligible evaluation dates: **362**.

- Selected gross payoff: **$982.62**.
- Same-cohort original linear: **$1,020.96**; always virtual load: **$1,384.92**.
- Increment over linear: **$-0.11/decision**, seven-day 95% interval **[$-0.69, $0.40]**.
- Increment over always-load: **$-1.11/decision**, interval **[$-8.28, $5.79]**.
- Raw gross mean versus flat interval: **[$-8.18, $18.20]**.
- Best day **2025-06-24**, payoff **$1,768.53**; remaining dates **$-785.91**. Positive months: **3 of 12**.

**Interpretation:** This comparison does not establish reliable incremental gross alpha over the original linear model and constant-direction benchmark.

### Validation selection and all alternatives


```csv
strategy,days,active_trades,virtual_load_days,virtual_supply_days,flat_days,total_gross_dollars,mean_daily_gross_dollars,mean_active_trade_dollars,win_rate_active,zero_payoff_active_trades,daily_std_dollars,best_day_dollars,worst_day_dollars,fifth_percentile_dollars,worst_five_percent_mean_dollars,max_drawdown_dollars
calendar,364,364,201,163,0,1728.4199999999996,4.748406593406592,4.748406593406592,0.4972527472527472,0,63.23519753128357,828.7299999999999,-132.61,-41.885499999999986,-71.12631578947368,630.5900000000015
linear,364,364,202,162,0,1647.2199999999998,4.52532967032967,4.52532967032967,0.489010989010989,0,63.25159810175118,828.7299999999999,-132.61,-41.885499999999986,-70.69,635.6100000000006
revision,364,364,193,171,0,1644.4799999999998,4.517802197802197,4.517802197802197,0.4862637362637362,0,63.252137686232565,828.7299999999999,-130.73000000000002,-42.784,-72.79736842105264,310.80999999999983
always_load,364,364,364,0,0,540.38,1.4845604395604397,1.4845604395604397,0.3571428571428571,0,63.39629086033012,828.7299999999999,-130.73000000000002,-44.910999999999994,-66.07105263157894,952.76
always_supply,364,364,0,364,0,-540.38,-1.4845604395604397,-1.4845604395604397,0.6428571428571429,0,63.39629086033012,130.73000000000002,-828.7299999999999,-49.039999999999985,-167.3736842105263,1799.44
flat,364,0,0,0,364,0.0,0.0,,,0,0.0,0.0,-0.0,0.0,0.0,0.0
training_mean,364,364,364,0,0,540.38,1.4845604395604397,1.4845604395604397,0.3571428571428571,0,63.39629086033012,828.7299999999999,-130.73000000000002,-44.910999999999994,-66.07105263157894,952.76
```

### Final strategy metrics (including unselected alternatives)

```csv
group_type,group,strategy,days,active_trades,virtual_load_days,virtual_supply_days,flat_days,total_gross_dollars,mean_daily_gross_dollars,mean_active_trade_dollars,win_rate_active,zero_payoff_active_trades,daily_std_dollars,best_day_dollars,worst_day_dollars,fifth_percentile_dollars,worst_five_percent_mean_dollars,max_drawdown_dollars,spread_mae_mwh,spread_rmse_mwh
overall,all,calendar,362,362,191,171,0,321.9800000000005,0.889447513812156,0.889447513812156,0.4281767955801105,0,113.66568351091794,1768.5300000000002,-302.82,-100.9645,-149.92526315789473,1660.6599999999994,37.62546358590256,112.93515840377592
overall,all,linear,362,362,195,167,0,1020.9600000000004,2.8203314917127087,2.8203314917127087,0.4447513812154696,0,113.63408209085948,1768.5300000000002,-233.7,-92.28549999999998,-138.89578947368423,983.0900000000004,37.43419435616741,112.63945963672772
overall,all,revision,362,362,195,167,0,982.6200000000008,2.714419889502764,2.714419889502764,0.4447513812154696,0,113.63666851340712,1768.5300000000002,-233.7,-92.28549999999998,-138.89578947368423,968.45,37.49276883842487,112.70387190016048
overall,all,always_load,362,362,362,0,0,1384.9200000000003,3.825745856353592,3.825745856353592,0.3314917127071823,0,113.60459515852304,1768.5300000000002,-233.7,-54.554,-112.09052631578948,1096.6700000000008,,
overall,all,always_supply,362,362,0,362,0,-1384.9200000000003,-3.825745856353592,-3.825745856353592,0.6685082872928176,0,113.60459515852304,233.7,-1768.5300000000002,-100.683,-287.3736842105263,2684.56,,
overall,all,flat,362,0,0,0,362,0.0,0.0,,,0,0.0,0.0,-0.0,0.0,0.0,0.0,,
overall,all,training_mean,362,362,362,0,0,1384.9200000000003,3.825745856353592,3.825745856353592,0.3314917127071823,0,113.60459515852304,1768.5300000000002,-233.7,-54.554,-112.09052631578948,1096.6700000000008,,
```

### All block-length sensitivity intervals

```csv
selected,benchmark,block_days,mean_increment,lower_95,upper_95
revision,linear,7,-0.1059116022099448,-0.689140791027155,0.4006286525475747
revision,linear,14,-0.1059116022099448,-0.6915003103004619,0.4077776046475835
revision,linear,28,-0.1059116022099448,-0.6276878453038676,0.3655260160975083
revision,calendar,7,1.824972375690608,-0.8470104337246137,5.959819007503455
revision,calendar,14,1.824972375690608,-0.756353897141639,5.6757508218802775
revision,calendar,28,1.824972375690608,-0.6335930402930405,5.581527596663552
revision,always_load,7,-1.1113259668508293,-8.276373307656396,5.787551073926071
revision,always_load,14,-1.1113259668508293,-8.311225740575559,5.5402160387954495
revision,always_load,28,-1.1113259668508293,-7.854296175799087,5.367340669122155
revision,flat,7,2.7144198895027634,-8.18026765736674,18.196556729588693
revision,flat,14,2.7144198895027634,-8.24592664759274,19.25521900823221
revision,flat,28,2.7144198895027634,-7.044574957310362,17.857237618479683
```

Data gate: 1809 eligible of 1,826 dates, 17 exclusions. No imputations or actual-future-weather substitution.

## Limits and stopping point

Same-cohort benchmarks are essential: excluding dates and refitting can change the original linear strategy's payoff. Do not compare these selected totals directly with the original 362-date $1,020.96 result. Gross dollars are not percentage returns. Operational forecast archive timestamps provide availability evidence, not a complete first-dissemination ledger. Corrected outcome prices do not recreate historical training-label or invoice vintages. One evaluation year, one grid point, heavy tails and omissions of price history/outages/fuel costs limit interpretation. Bootstrap intervals do not cover researcher choices or future-year performance.

Both fixed tests are complete. No interaction search, tuning to 2025 or automatic next hypothesis follows. A new prospective evaluation would be needed before increasing confidence in any signal.

## Reproduction and source evidence

`src/acquire_revisions.py` retrieves bounded temperature-message ranges from the public NOAA HRRR S3 archive. Prior forecast gates, NYISO price archives and market documentation are retained in the adjacent original studies. Run the family preparation/model scripts and tests described in the folder README. The frozen `EXPERIMENT.md` defines features, cohorts, selection and stopping rules. Raw receipts, availability metadata, family exclusions, daily signals and source/code hashes are retained. Chart PNGs are inspected separately; full browser layout is not certified.
