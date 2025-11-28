	object_const_def
	const_export ROUTE1_YOUNGSTER1
	const_export ROUTE1_YOUNGSTER2

Route1_Object:
	db $b ; border block

	def_warp_events

	def_bg_events
	bg_event  9, 27, TEXT_ROUTE1_SIGN

	def_object_events
	
	def_warps_to ROUTE_1

	; unused
	warp_to 2, 7, 4
