import React from 'react'
import { Button } from './button'
const Header = () => {
    return (
        <header>
            <a className=""><h3><span>DZ</span>-KITAB</h3></a>
            <div className="links">
                <a>Home</a>
                <a>About us</a>
                <a>Contact us</a>
            </div>
            <div className="buttons">
                {/* <Button width='80px' height='30px' text="Login" backgroundcolor={'#1314D7'} color={`white`}   borderadius={'10px'}></Button>
                <Button width='80px' height='30px' text="Register" color={`black`} bordercolor='#1314D7' borderadius={'10px'}></Button> */}
                <button className='login-button'>Login</button>
                <button className='register-button'>Register</button>
            </div>
        </header>   
    )
}

export default Header