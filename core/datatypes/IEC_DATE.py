from __future__ import annotations

import datetime

from core.datatypes.IEC_ANY import DataTypeIDEnum, IEC_ANY_DATE
from core.datatypes.IEC_Literals import parse_iec_date_literal


class IEC_DATE(IEC_ANY_DATE):
	"""Calendar date"""

	@classmethod
	def type_id(cls) -> DataTypeIDEnum:
		return DataTypeIDEnum.DATE

	def _default(self) -> datetime.date:
		return datetime.date(1970, 1, 1)

	def _coerce(self, value) -> datetime.date:
		if isinstance(value, datetime.datetime):
			return value.date()
		if isinstance(value, datetime.date):
			return value
		if isinstance(value, str):
			return parse_iec_date_literal(value)
		raise TypeError("Unsupported value type for IEC_DATE")
