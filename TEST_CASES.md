# Test Case Specification: "Тектоник"

Тесты написаны для роли A и являются исполняемым уточнением `SPEC.md`.
Каждый метод теста содержит ID соответствующего кейса в docstring. Модульные
кейсы используют AAA, сценарные - GWT через обёртку `TectonicPilot`.

Соотношение: 22 модульных кейса и 4 сценарных кейса, то есть примерно 85/15.

## Модульные тесты

| ID | Источник | Предусловие | Вход | Ожидание | Приоритет | Тест |
| --- | --- | --- | --- | --- | --- | --- |
| TC-01 | SPEC 3.2 | - | `name="   "` | `ValueError` | high | `test_init_rejects_empty_name` |
| TC-02 | SPEC 3.2 | - | `mass_kg=0`, `drill_diameter_m=0`, `max_speed_kmh=0` | `ValueError` для каждого значения | high | `test_init_rejects_nonpositive_dimensions` |
| TC-03 | SPEC 3.2 | - | `energy=-1`, `energy=101` | `ValueError` | high | `test_init_validates_energy_and_default` |
| TC-04 | SPEC 3.3 | созданный транспорт | конструктор без `energy` | `energy == 100`, `position_km == 0`, `is_drilling is False` | high | `test_initial_state_is_origin_and_not_drilling` |
| TC-05 | SPEC 3.4.1 | energy=100, speed=50 | `move(20, "ground")` | время `0.4`, позиция `20`, энергия `80`, бурение `False` | high | `test_move_ground_updates_state` |
| TC-06 | SPEC 3.4.1 | energy=50, speed=40 | `move(10, "tunnel")` | время `10/24`, позиция `10`, энергия `20`, бурение `True` | high | `test_move_tunnel_uses_boring_rules` |
| TC-07 | SPEC 3.4.1 | созданный транспорт | `move(0, "ground")`, неизвестный terrain | `ValueError` | high | `test_move_rejects_invalid_arguments` |
| TC-08 | SPEC 3.4.1, 6 | energy=50, position=10 | `move(3, "water")` | `MoleCannotSwim`, состояние не меняется | high | `test_move_water_raises_domain_error` |
| TC-09 | SPEC 3.4.1, 6 | energy=10 | `move(5, "tunnel")` | `MoleNoEnergy`, состояние не меняется | high | `test_move_rejects_insufficient_energy_without_mutation` |
| TC-10 | SPEC 5 | energy=50 | `move(50, "ground")` | успех, энергия `0`, позиция `50` | high | `test_move_allows_exact_zero_energy` |
| TC-11 | SPEC 3.4.3 | energy=1, position=4, tunnel=False | `calculate_energy(10, "ground")`, `calculate_energy(4, "tunnel")` | `10` и `12`, состояние не меняется | high | `test_calculate_energy_is_pure` |
| TC-12 | SPEC 3.4.3 | созданный транспорт | нулевое расстояние, неизвестная среда, water | `ValueError`/`MoleCannotSwim` | high | `test_calculate_energy_rejects_invalid_arguments` |
| TC-13 | SPEC 3.4.2, сценарий 4 | drill=2.0, energy=40 | boulder, landslide, ravine | `True` для всех трёх, состояние не меняется | medium | `test_can_overcome_boulder_and_ravine` |
| TC-14 | SPEC 3.4.2 | drill=2.0 | energy `29`, затем `30` | landslide `False`, затем `True` | medium | `test_can_overcome_landslide_depends_on_energy` |
| TC-15 | SPEC 3.4.2 | созданный транспорт | `can_overcome("wall")` | `ValueError` | medium | `test_can_overcome_rejects_unknown_obstacle` |
| TC-16 | SPEC 3.4.4, 5 | energy=50 | `refuel(20)`, затем `refuel(1000)` | `70`, затем ровно `100` | high | `test_refuel_adds_and_caps_energy` |
| TC-17 | SPEC 3.4.4 | созданный транспорт | `refuel(0)`, `refuel(-1)` | `ValueError`, энергия не меняется | high | `test_refuel_rejects_nonpositive_amount` |
| TC-18 | SPEC 3.4.5 | транспорт после move | изменить и удалить значения снимка | ровно пять ключей; изменения снимка не меняют объект и следующий снимок | high | `test_get_status_returns_expected_snapshot` |
| TC-19 | SPEC 6 | - | классы `MoleNoEnergy`, `MoleCannotSwim` | наследуются от `CrazyVehicleError` и `TectonicMoleError` | medium | `test_domain_exceptions_have_expected_hierarchy` |
| TC-20 | SPEC 3.2 | - | строковое имя, положительные параметры, energy=0 | объект создан | medium | `test_init_accepts_lower_energy_boundary` |
| TC-25 | SPEC 3.2, 3.4.1, 3.4.3, 3.4.4 | созданный транспорт | неверные типы, `bool`, `NaN`, бесконечность; числовые `int`/`float` | `TypeError` для неверного типа и `ValueError` для non-finite; состояние не меняется | high | `test_numeric_input_contract` |
| TC-26 | SPEC 3.4.2 | положительные параметры | диаметры `0.99/1.0/1.01` для boulder и `1.99/2.0/2.01` для ravine | `False/True/True` на каждой границе | high | `test_obstacle_diameter_thresholds` |

## Сценарные тесты

| ID | Источник | Вход и шаги | Ожидание | Приоритет | Тест |
| --- | --- | --- | --- | --- | --- |
| TC-21 | SPEC 4.2.1 | пилот едет 10 км, бурит 6 км, заправляет 50 и едет 4 км | итог: position `20`, energy `88`, `is_drilling=False` | high | `test_TC_21_tunnel_under_railway` |
| TC-22 | SPEC 4.2.2 | пилот с energy=25 проверяет препятствия, заправляется на 10, едет 5 км и бурит 5 км | валун/оползень/овраг дают `True`/`True`/`False` до движения, итог: position `10`, energy `15` | high | `test_TC_22_escape_landslide` |
| TC-23 | SPEC 4.2.3 | пилот бурит 6 км при energy=20, повторяет 1 км, заправляет 10, едет 2 км | `MoleNoEnergy` на втором бурении, итог: position `8`, energy `10`, бурение `False` | high | `test_TC_23_emergency_energy_reserve` |
| TC-24 | SPEC 4.2.4 | пилот едет 10 км, пытается ехать по воде 3 км, затем едет 5 км | `MoleCannotSwim`, итог: position `15`, energy `35` | high | `test_TC_24_water_on_route` |
