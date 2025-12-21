import React from 'react'

export const MessageCard = ({name,last_message,time}) => {
    return (
        <div className='message-card ' >
            <div className="">
                <img src=''></img>
            </div>
            <div className="">
                <p>{name}</p>
                <p>{last_message}</p>
            </div>
            <p>{time}</p>
        </div>
    )
}
