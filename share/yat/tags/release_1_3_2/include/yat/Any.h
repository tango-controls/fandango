/*!
 * \file    
 * \brief   
 * \author stolen from the Boost library - Copyright Kevlin Henney, 2000, 2001, 2002. All rights reserved.
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_ANY_H_
#define _YAT_ANY_H_

#include <typeinfo>
#include <yat/CommonHeader.h>

namespace yat
{
    class Any
    {
    public:

        Any ()
          : m_content(0)
        {
          //- noop ctor
        }

        template<typename ValueType> 
		    Any (const ValueType & value)
          : m_content (new Holder<ValueType>(value))
        {
          //- noop ctor
        }

        Any (const Any & src)
          : m_content (src.m_content ? src.m_content->clone() : 0)
        {
          //- noop ctor
        }

        ~Any()
        {
			    delete m_content;
        }

        Any & swap (Any & src)
        {
            std::swap(m_content, src.m_content);
            return *this;
        }

        template<typename ValueType> 
		    Any & operator= (const ValueType & src)
        {
            Any(src).swap(*this);
            return *this;
        }

        Any & operator= (const Any & src)
        {
            Any(src).swap(*this);
            return *this;
        }

        bool empty() const
        {
            return ! m_content;
        }

        const std::type_info & type() const
        {
            return m_content ? m_content->type() : typeid(void);
        }

        class Placeholder
        {
        public:
            virtual ~Placeholder() 
            {
              //- noop ctor
            }
        public:
            virtual const std::type_info & type() const = 0;
            virtual Placeholder * clone() const = 0;
        };

        template<typename ValueType>
        class Holder : public Placeholder
        {
        public:
            Holder (const ValueType & value)
              : m_held (value)
            {
              //- noop ctor
            }
			
            virtual const std::type_info & type() const
            {
				      return typeid(ValueType);
            }

            virtual Placeholder * clone() const
            {
                return new Holder(m_held);
            }

            ValueType m_held;
        };
		
        Placeholder * m_content;
    };

    class bad_any_cast : public std::bad_cast
    {
    public:
        virtual const char * what() const throw()
        {
            return "yat::Any conversion failed using yat::any_cast";
        }
    };

    template<typename ValueType>
    ValueType * any_cast (Any * operand)
    {
        return operand && operand->type() == typeid(ValueType)
                  ? &static_cast<Any::Holder<ValueType> *>(operand->m_content)->m_held
                  : 0;
    }

    template<typename ValueType>
    const ValueType * any_cast (const Any * operand)
    {
        return any_cast<ValueType>(const_cast<Any *>(operand));
    }

    template<typename ValueType>
    ValueType any_cast (const Any & operand) throw (yat::Exception)
    {
        const ValueType * result = any_cast<ValueType>(&operand);
		
        if (! result)
          THROW_YAT_ERROR(_CPTC("yat::any_cast error"),
                          _CPTC("yat::any_cast conversion failed"),
                          _CPTC("yat::any_cast"));
			
        return *result;
    }

    template<typename ValueType>
    ValueType any_cast (Any & operand) throw (yat::Exception)
    {
        ValueType * result = any_cast<ValueType>(&operand);
		
        if (! result)
          THROW_YAT_ERROR(_CPTC("yat::any_cast error"),
                          _CPTC("yat::any_cast conversion failed"),
                          _CPTC("yat::any_cast"));
			
        return *result;
    }

    template<typename ValueType>
    inline ValueType * unsafe_any_cast (Any * operand)
    {
        return &static_cast<Any::Holder<ValueType> *>(operand->m_content)->m_held;
    }

    template<typename ValueType>
    inline const ValueType * unsafe_any_cast (const Any * operand)
    {
        return unsafe_any_cast<ValueType>(const_cast<Any *>(operand));
    }
	
} //- namespace

#endif //- _YAT_ANY_H_



