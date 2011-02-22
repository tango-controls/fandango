/*!
 * \file    MessageQ.i
 * \brief   Inlined code of the YAT message queue class.
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

namespace yat
{

// ============================================================================
// MessageQ::periodic_tmo_expired
// ============================================================================
YAT_INLINE bool MessageQ::periodic_tmo_expired (double _tmo_msecs) const
{
  Timestamp now; 
  _GET_TIME(now);
  return _ELAPSED_MSEC(this->last_periodic_msg_ts_, now) >= (0.95 * _tmo_msecs);
}

// ============================================================================
// MessageQ::lo_wm
// ============================================================================
YAT_INLINE void MessageQ::lo_wm (size_t _lo_wm)
{
  this->lo_wm_ = _lo_wm;  

  if (this->lo_wm_ < kMIN_LO_WATER_MARK)
    this->lo_wm_ = kMIN_LO_WATER_MARK;

  if ((this->hi_wm_ - this->lo_wm_) < kMIN_WATER_MARKS_DIFF)
    this->hi_wm_ = this->lo_wm_ + kMIN_WATER_MARKS_DIFF;
}

// ============================================================================
// MessageQ::lo_wm
// ============================================================================
YAT_INLINE size_t MessageQ::lo_wm ()  const
{
  return this->lo_wm_;
}

// ============================================================================
// MessageQ::hi_wm
// ============================================================================
YAT_INLINE void MessageQ::hi_wm (size_t _hi_wm)
{
  this->hi_wm_ = _hi_wm;

  if ((this->hi_wm_ - this->lo_wm_) < kMIN_WATER_MARKS_DIFF)
    this->hi_wm_ = this->lo_wm_ + kMIN_WATER_MARKS_DIFF;
}

// ============================================================================
// MessageQ::hi_wm
// ============================================================================
YAT_INLINE size_t MessageQ::hi_wm ()  const
{
  return this->hi_wm_;
}

// ============================================================================
// MessageQ::throw_on_post_msg_timeout
// ============================================================================
YAT_INLINE void MessageQ::throw_on_post_msg_timeout (bool _strategy)
{
  this->throw_on_post_msg_timeout_ = _strategy;
}

// ============================================================================
// MessageQ::clear
// ============================================================================
YAT_INLINE void MessageQ::clear (void)
{
  YAT_TRACE("MessageQ::clear");

  yat::AutoMutex<> guard(this->lock_);

  this->clear_i();
}

} //- namespace
