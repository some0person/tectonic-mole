"""Реализация гусеничного крота "Тектоник" по SPEC.md v1.0 (роль D).
"""

from __future__ import annotations

import math
from typing import Any


class CrazyVehicleError(Exception):
    """Базовое доменное исключение для всех безумных транспортов."""


class TectonicMoleError(CrazyVehicleError):
    """Базовое исключение для "Тектоника"."""


class MoleNoEnergy(TectonicMoleError):
    """Недостаточно энергии для перемещения."""


class MoleCannotSwim(TectonicMoleError):
    """Попытка перемещения по воде."""


_TERRAINS = ("ground", "tunnel", "water")
_OBSTACLES = ("boulder", "landslide", "ravine")
_ENERGY_MIN = 0.0
_ENERGY_MAX = 100.0


def _is_number(value: Any) -> bool:
    """True для int/float, кроме bool."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_finite(value: Any, field: str) -> float:
    """Проверяет числовой вход и возвращает float.

    TypeError — неверный тип (включая bool и нечисловые типы).
    ValueError — NaN или бесконечность.
    """
    if not _is_number(value):
        raise TypeError(f"{field} must be int or float, got {type(value).__name__}")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{field} must be finite, got {number!r}")
    return number


def _validate_terrain(terrain: Any) -> str:
    if not isinstance(terrain, str):
        raise TypeError(f"terrain must be str, got {type(terrain).__name__}")
    if terrain not in _TERRAINS:
        raise ValueError(f"unknown terrain: {terrain!r}")
    return terrain


def _validate_obstacle(obstacle: Any) -> str:
    if not isinstance(obstacle, str):
        raise TypeError(f"obstacle must be str, got {type(obstacle).__name__}")
    if obstacle not in _OBSTACLES:
        raise ValueError(f"unknown obstacle: {obstacle!r}")
    return obstacle


class TectonicMole:
    """Одноместный гусеничный транспорт с вращающимся буром (стихия: земля)."""

    def __init__(
        self,
        name: str,
        mass_kg: float,
        drill_diameter_m: float,
        max_speed_kmh: float,
        energy: float = 100.0,
    ) -> None:
        if not isinstance(name, str):
            raise TypeError(f"name must be str, got {type(name).__name__}")
        if not name.strip():
            raise ValueError("name must be a non-empty string")

        mass = _validate_finite(mass_kg, "mass_kg")
        drill = _validate_finite(drill_diameter_m, "drill_diameter_m")
        speed = _validate_finite(max_speed_kmh, "max_speed_kmh")
        energy_value = _validate_finite(energy, "energy")

        if mass <= 0:
            raise ValueError("mass_kg must be > 0")
        if drill <= 0:
            raise ValueError("drill_diameter_m must be > 0")
        if speed <= 0:
            raise ValueError("max_speed_kmh must be > 0")
        if not (_ENERGY_MIN <= energy_value <= _ENERGY_MAX):
            raise ValueError("energy must be in [0, 100]")

        self.name: str = name
        self.mass_kg: float = mass
        self.drill_diameter_m: float = drill
        self.max_speed_kmh: float = speed
        self.energy: float = energy_value
        self.position_km: float = 0.0
        self.is_drilling: bool = False


    def _validate_distance(self, distance_km: Any) -> float:
        distance = _validate_finite(distance_km, "distance_km")
        if distance <= 0:
            raise ValueError("distance_km must be > 0")
        return distance

    def _speed_for(self, terrain: str) -> float:
        if terrain == "ground":
            return self.max_speed_kmh
        return self.max_speed_kmh * 0.6  # tunnel

    def _cost_for(self, distance_km: float, terrain: str) -> float:
        if terrain == "ground":
            return distance_km * 1.0
        return distance_km * 3.0  # tunnel


    def move(self, distance_km: float, terrain: str) -> float:
        """Перемещает транспорт и возвращает время в часах.

        Состояние меняется только после успешной проверки всех условий.
        """
        distance = self._validate_distance(distance_km)
        terrain_value = _validate_terrain(terrain)

        if terrain_value == "water":
            raise MoleCannotSwim("tectonic mole cannot move through water")

        cost = self._cost_for(distance, terrain_value)
        if self.energy < cost:
            raise MoleNoEnergy(
                f"not enough energy: required {cost}, have {self.energy}"
            )

        speed = self._speed_for(terrain_value)
        elapsed_hours = distance / speed

        self.position_km += distance
        self.energy -= cost
        if self.energy < 0 and self.energy > -1e-9:
            self.energy = 0.0
        self.is_drilling = terrain_value == "tunnel"
        return elapsed_hours

    def can_overcome(self, obstacle: str) -> bool:
        """Проверяет преодолимость препятствия без изменения состояния."""
        obstacle_value = _validate_obstacle(obstacle)
        if obstacle_value == "boulder":
            return self.drill_diameter_m >= 1.0
        if obstacle_value == "landslide":
            return self.energy >= 30.0
        return self.drill_diameter_m >= 2.0  

    def calculate_energy(self, distance_km: float, terrain: str) -> float:
        """Рассчитывает расход энергии без изменения состояния."""
        distance = self._validate_distance(distance_km)
        terrain_value = _validate_terrain(terrain)
        if terrain_value == "water":
            raise MoleCannotSwim("tectonic mole cannot move through water")
        return self._cost_for(distance, terrain_value)

    def refuel(self, amount: float) -> None:
        """Пополняет энергию, не превышая 100.0."""
        amount_value = _validate_finite(amount, "amount")
        if amount_value <= 0:
            raise ValueError("amount must be > 0")
        self.energy = min(self.energy + amount_value, _ENERGY_MAX)

    def get_status(self) -> dict:
        """Возвращает независимый снимок публичного состояния."""
        return {
            "name": self.name,
            "energy": self.energy,
            "position_km": self.position_km,
            "is_drilling": self.is_drilling,
            "drill_diameter_m": self.drill_diameter_m,
        }
