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
