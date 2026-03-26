from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EntityType(str, Enum):
    MERCHANTS = "merchants"
    CUSTOMERS = "customers"
    PAYMENTS = "payments"
    ORDERS = "orders"
    TRANSACTIONS = "transactions"
    PAYOUTS = "payouts"
    DISPUTES = "disputes"


TABLE_NAMES: dict[EntityType, dict[str, str]] = {
    EntityType.MERCHANTS: {
        "bronze": "psp_merchants",
        "silver": "psp_merchants",
        "gold": "psp_merchant_performance",
    },
    EntityType.CUSTOMERS: {
        "bronze": "psp_customers",
        "silver": "psp_customers",
        "gold": "psp_customer_analytics",
    },
    EntityType.PAYMENTS: {
        "bronze": "psp_payment_instruments",
        "silver": "psp_payment_instruments",
        "gold": None,
    },
    EntityType.ORDERS: {
        "bronze": "psp_orders",
        "silver": "psp_orders",
        "gold": None,
    },
    EntityType.TRANSACTIONS: {
        "bronze": "psp_transactions",
        "silver": "psp_transactions",
        "gold": "psp_risk_fraud_monitoring",
    },
    EntityType.PAYOUTS: {
        "bronze": "psp_payouts",
        "silver": "psp_payouts",
        "gold": None,
    },
    EntityType.DISPUTES: {
        "bronze": "psp_disputes",
        "silver": "psp_disputes",
        "gold": None,
    },
}

CATALOGS: dict[str, str] = {
    "dev": "psp",
    "prd": "psp_prd",
}

DATABRICKS_HOSTS: dict[str, str] = {
    "dev": "https://adb-2090585310411504.4.azuredatabricks.net",
    "prd": "https://adb-2090585310411504.4.azuredatabricks.net",
}


@dataclass(frozen=True)
class FlowConfig:
    entity: EntityType
    env: str = "dev"
    storage_account: str = "owshqblobstg"
    container: str = "payment-service-provider"

    @property
    def catalog(self) -> str:
        return CATALOGS.get(self.env, f"psp_{self.env}")

    @property
    def databricks_host(self) -> str:
        return DATABRICKS_HOSTS.get(self.env, DATABRICKS_HOSTS["dev"])

    @property
    def pipeline_name(self) -> str:
        return f"psp-analytics-{self.env}"

    @property
    def blob_prefix(self) -> str:
        return f"{self.entity.value}/"

    @property
    def volume_path(self) -> str:
        return f"/Volumes/{self.catalog}/analytics/vol-landing-zone/{self.entity.value}"

    @property
    def abfss_path(self) -> str:
        return f"abfss://{self.container}@{self.storage_account}.dfs.core.windows.net/{self.entity.value}/"

    def table_name(self, layer: str) -> str | None:
        return TABLE_NAMES[self.entity].get(layer)

    def full_table_name(self, layer: str) -> str | None:
        table = self.table_name(layer)
        if table is None:
            return None
        return f"`{self.catalog}`.`{layer}`.`{table}`"

    @staticmethod
    def all_entities() -> list[EntityType]:
        return list(EntityType)
