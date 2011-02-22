/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_CALLBACK_H_
#define _YAT_CALLBACK_H_

#include <yat/CommonHeader.h>

namespace yat 
{

  template <class Param>
  class CallbackContainer
  {
  public:
    //! destructor
    virtual ~CallbackContainer<Param>()
    {};

    //! do operation with Param as argument
    virtual void operator()(Param) const = 0;

    //! deep copy
    virtual CallbackContainer<Param>* clone() const = 0;

  };

  template <class Param> 
  class Callback
  {
  public:
    //! constructor
    Callback( CallbackContainer<Param>* c )
      : container(c)
    {};

    //! constructor
    Callback( const Callback<Param>& c )
      : container(c.container ? c.container->clone() : NULL)
    {};

    //! destructor
    ~Callback()
    {
      delete this->container;
      this->container = NULL;
    };

    Callback<Param>& operator = ( const Callback<Param>& callback )
    {
      if (this != &callback)
      {
        delete this->container;
        this->container =  callback.container ? callback.container->clone() : NULL;
      }
      return *this;
    };

    //! do operation defined in body
    void operator()(Param p) 
    {
      if (this->container)
        (*this->container)(p);
      else
        THROW_YAT_ERROR("NULL_POINTER", "Null callback called", "Callback::operator()(Param p)");
    }
    
    //!  
    bool  is_empty (void) const
    {
      return this->container == NULL;
    };

  private:
    CallbackContainer<Param>* container;
  };


  template <class Param, class Function>
  class Function_CallbackContainer : public CallbackContainer<Param>
  {
  public:
    //! constructor taking a function pointer
    Function_CallbackContainer( const Function& function )
      : function_(function)
    {}

    //! execute operation: call the function
    void operator()(Param p) const 
    { 
      if (function_) 
        function_( p );
    }

    //! virtual copy constructor
    CallbackContainer<Param>* clone() const
    {
      return new Function_CallbackContainer<Param,Function>(*this); 
    }

  private:
    //! the callback function
    const Function function_;

    //! no assignemt operator
    Function_CallbackContainer& operator=(Function_CallbackContainer&);
  };


  template <class Param, class Client, class Member>
  class Member_CallbackContainer : public CallbackContainer<Param>
  {
  public:
    //! Member function type
    typedef void (Client::*PMEMBERFUNC)(Param);


    //! constructor taking a function pointer
    Member_CallbackContainer( Client& client, Member member )
      : client_(client),
        member_func_(member)
    {}

    //! execute operation: call the function
    void operator()(Param p) const 
    { 
      if (member_func_) 
        (client_.*member_func_)( p );
    }

    //! virtual copy constructor
    CallbackContainer<Param>* clone() const
    {
      return new Member_CallbackContainer<Param, Client, Member>(*this); 
    }

  private:
    //! The object the method function belongs to
    Client& client_;

    //! The method to call
    PMEMBERFUNC member_func_;

    //! no assignement operator
    Member_CallbackContainer& operator=(Member_CallbackContainer&);
  };

# define YAT_DEFINE_CALLBACK( CallbackClassName, Param ) \
  template <class Function> \
  class Function_ ## CallbackClassName ## Container : public yat::Function_CallbackContainer<Param, Function> \
  { \
    typedef yat::Function_CallbackContainer<Param, Function> InHerited; \
  public: \
    Function_##CallbackClassName##Container( Function function ) \
     : InHerited( function ) \
     {} \
  }; \
  template <class Client, class Member> \
  class Member_   ## CallbackClassName ## Container : public yat::Member_CallbackContainer<Param, Client, Member> \
  { \
    typedef yat::Member_CallbackContainer<Param, Client, Member> InHerited; \
  public: \
    Member_##CallbackClassName##Container( Client& client, Member member ) \
     : InHerited( client, member ) \
     {} \
  }; \
  class CallbackClassName : public yat::Callback<Param> \
  { \
    typedef yat::Callback<Param> InHerited; \
  public: \
    CallbackClassName( yat::CallbackContainer<Param> *container = 0) \
      : InHerited(container) \
    {} \
    CallbackClassName( const CallbackClassName& cb ) \
      : InHerited(cb) \
    {} \
    CallbackClassName& operator=( const CallbackClassName& cb ) \
    { \
      InHerited::operator =(cb); \
      return *this; \
    } \
    \
    template <class Function> \
    static CallbackClassName instanciate( Function function ) \
    { \
      return new Function_ ## CallbackClassName ## Container<Function>( function ); \
    } \
    template <class Client, class Member> \
    static CallbackClassName instanciate( Client& client, Member member ) \
    { \
      return new Member_   ## CallbackClassName ## Container<Client, Member>( client, member ); \
    } \
  }; \


  



} // namespace

#endif



