"""Quell-Parser für die Redaktions-Pipeline.

Jede Quelle hat ein eigenes Modul, das eine `Parser`-Klasse mit
`parse() -> list[CandidateData]` exportiert. Auswahl erfolgt über
den `parser_key`-Feldwert in NewsSource (FQDN der Parser-Klasse).
"""
