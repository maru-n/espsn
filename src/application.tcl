#====================
# InputFlowDuty
#====================
Class Application/InputFlowDuty -superclass Application/FTP

Application/InputFlowDuty instproc init {args} {
  global ns
  $self instvar process_list state duty_l duty_h cycle state
  set process_list [lindex $args 0]
  $ns at 0.0 "$self start"
  foreach process $process_list {
    set time [lindex $process 0]
    set state_id [lindex $process 1]
    if { $state_id == 0 } {
      $ns at "$time" "$self input_off"
    } else {
      $ns at "$time" "$self input_on"
    }
  }
  set cycle 0.1
  set duty_l 0.3
  set duty_h 0.6
  set state 1
  set input_state 1
  eval $self next
}

Application/InputFlowDuty instproc input_on {} {
  $self instvar input_state
  set input_state 1
}

Application/InputFlowDuty instproc input_off {} {
  $self instvar input_state
  set input_state 0
}


Application/InputFlowDuty instproc run {} {
  global ns
  $self instvar cycle duty_l duty_h state input_state

  set now [$ns now]

  if {$state == 0} {
    # puts [format "%s: start at %f" $self $now]
    eval $self start
    set state 1
    if {$input_state == 1} {
      $ns at [expr $now + $cycle * $duty_h] "$self run"
    } else {
      $ns at [expr $now + $cycle * $duty_l] "$self run"
    }
  } else {
    # puts [format "%s: stop at %f" $self $now]
    eval $self stop
    set state 0
    if {$input_state == 1} {
      $ns at [expr $now + $cycle * (1 - $duty_h)] "$self run"
    } else {
      $ns at [expr $now + $cycle * (1 - $duty_l)] "$self run"
    }

  }
}



#====================
# InputFlow
#====================
Class Application/InputFlow -superclass Application/FTP

Application/InputFlow instproc init {args} {
  global ns
  $self instvar process_list
  set process_list [lindex $args 0]
  $ns at 0.0 "$self start"
  foreach process $process_list {
    set time [lindex $process 0]
    set state_id [lindex $process 1]
    if { $state_id == 0 } {
      $ns at "$time" "$self stop"
    } else {
      $ns at "$time" "$self start"
    }
  }
  eval $self next
}


#====================
# InputFlowReverse
#====================
Class Application/InputFlowReverse -superclass Application/FTP

Application/InputFlowReverse instproc init {args} {
  global ns
  $self instvar process_list
  set process_list [lindex $args 0]
  $ns at 0.0 "$self start"
  foreach process $process_list {
    set time [lindex $process 0]
    set state_id [lindex $process 1]
    if { $state_id == 0 } {
      $ns at "$time" "$self start"
    } else {
      $ns at "$time" "$self stop"
    }
  }
  eval $self next
}


#====================
# InputRealtimeFlow
#====================
Class Application/InputRealtimeFlow -superclass Application/FTP
Application/InputRealtimeFlow instproc input_on {} {
    $self start
}
Application/InputRealtimeFlow instproc input_off {} {
    $self stop
}


#====================
# InputRealtimeFlowReverse
#====================
Class Application/InputRealtimeFlowReverse -superclass Application/FTP
Application/InputRealtimeFlowReverse instproc input_on {} {
    $self stop
}
Application/InputRealtimeFlowReverse instproc input_off {} {
    $self start
}



#====================
# PeriodicFTP
#====================
Class Application/PeriodicFTP -superclass Application/FTP

Application/PeriodicFTP instproc init {args} {
  $self instvar cycle duty state
  set cycle [lindex $args 0]
  set duty [lindex $args 1]
  set state 0
  eval $self next
}

Application/PeriodicFTP instproc run {} {
  global ns
  $self instvar cycle duty state

  set now [$ns now]

  if {$state == 0} {
    # puts [format "%s: start at %f" $self $now]
    eval $self start
    set state 1
    $ns at [expr $now + $cycle * $duty] "$self run"
  } else {
    # puts [format "%s: stop at %f" $self $now]
    eval $self stop
    set state 0
    $ns at [expr $now + $cycle * (1 - $duty)] "$self run"
  }
}
