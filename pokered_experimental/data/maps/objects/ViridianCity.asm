	object_const_def
	const_export VIRIDIANCITY_YOUNGSTER1
	const_export VIRIDIANCITY_GAMBLER1
	const_export VIRIDIANCITY_YOUNGSTER2
	const_export VIRIDIANCITY_GIRL
	const_export VIRIDIANCITY_OLD_MAN_SLEEPY
	const_export VIRIDIANCITY_FISHER
	const_export VIRIDIANCITY_OLD_MAN

ViridianCity_Object:
	db $f ; border block

	def_warp_events
	warp_event 23, 25, VIRIDIAN_POKECENTER, 1
	warp_event 29, 19, VIRIDIAN_MART, 1
	warp_event 21, 15, VIRIDIAN_SCHOOL_HOUSE, 1
	warp_event 21,  9, VIRIDIAN_NICKNAME_HOUSE, 1
	; DISABLED FOR WALKER: Prevent entering Viridian Gym
	; warp_event 32,  7, VIRIDIAN_GYM, 1

	def_bg_events
	bg_event 17, 17, TEXT_VIRIDIANCITY_SIGN
	bg_event 19,  1, TEXT_VIRIDIANCITY_TRAINER_TIPS1
	bg_event 21, 29, TEXT_VIRIDIANCITY_TRAINER_TIPS2
	bg_event 30, 19, TEXT_VIRIDIANCITY_MART_SIGN
	bg_event 24, 25, TEXT_VIRIDIANCITY_POKECENTER_SIGN
	bg_event 27,  7, TEXT_VIRIDIANCITY_GYM_SIGN

	def_object_events
	
	def_warps_to VIRIDIAN_CITY
