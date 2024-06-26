import { useState, useEffect } from 'react';
import { Form } from 'react-router-dom';
import { apiUrl } from '../../auth/Auth';
import Spinner from '../../Spinner';
import WeatherNow from './WeatherNow';
import WeatherForTheDay from './WeatherForTheDay';
import WeatherForTheWeek from './WeatherForTheWeek';
import WeatherMessage from './WeatherMessage';
import { getIconHref } from './WeatherUtils';
import '../css/Weather.min.css';

function getPeriodOption(): string {
    const tmp: string | null = localStorage.getItem('weather-period');
    let ret: string = 'now';
    if (tmp != null) {
        ret = tmp;
    }
    return ret;
}

function getBrsrLocOption(): boolean {
    const ubl = localStorage.getItem('weather-use-browser-location');
    if (ubl === undefined)
        return true;
    return (ubl === 'true');
}

function getLocationOption() {
    const lctn = localStorage.getItem('weather-location');
    if (lctn === undefined)
        return '';
    return lctn;
}

export default function Weather({screenWidth}: {screenWidth: number}) {
    function setPeriodOption(value: string): void {
        setPeriod(value);
        localStorage.setItem('weather-period', value);
    }
    
    const [period, setPeriod] = useState(getPeriodOption());
    const [values, setValues] = useState<any>(null);
    const [message, setMessage] = useState('');
    const [status, setStatus] = useState('init');
    const [brsrLoc, setBrsrLoc] = useState(getBrsrLocOption());
    const [location, setLocation] = useState(getLocationOption());

    useEffect(() => {

        async function getCoord() {
            const pos: any = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject);
            });
          
            return {
                lat: pos.coords.latitude,
                lon: pos.coords.longitude,
            };
        }

        async function getData() {
            setStatus('updating');
            let loc, lat, lon;

            if (!brsrLoc) {
                loc = location;
                lat = '';
                lon = '';
            }
            else {
                loc = '';
                const coord = await getCoord();
                lat = coord.lat;
                lon = coord.lon;
            }

            if (!loc && !lat && ! lon) {
                setStatus('mess');
                setMessage('Define the location.');
            }
            else{
                const url = apiUrl + `api/get_chart_data/?mark=weather&version=v2&location=${loc}&lat=${lat}&lon=${lon}`;
                const cred: RequestCredentials = 'include';
                const options = {
                    method: 'GET',
                    headers: {'Content-type': 'application/json'},
                    credentials: cred,
                };
                const response = await fetch(url, options);
                if (response.ok) {
                    let resp_data = await response.json();
                    if (resp_data) {
                        setValues(resp_data.data);
                        if (resp_data.result === 'ok')
                            setStatus('ready');
                        else {
                            setStatus('mess');
                            setMessage(resp_data.procedure + ': ' + resp_data.info);
                        }
                    }
                }
            }
        }

        getData();
    }, [brsrLoc, location]);

    function onChangeBrsrLoc(e: any) {
        const checked = e.target.checked;
        setBrsrLoc(checked);
        localStorage.setItem('weather-use-browser-location', checked.toString());
    }

    function handleSubmit(e: any) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        const formJson = Object.fromEntries(formData.entries());
        const newLocation: string = formJson.location.toString();
        setLocation(newLocation);
        localStorage.setItem('weather-location', newLocation);
    }

    const widgetWidth = screenWidth < 600 ? 410 : (screenWidth < 768 ? 500 : 600);
    const widgetHeight = screenWidth < 600 ? 200 : (screenWidth < 768 ? 250 : 300);

    const cr_info = (values && values.cr_info) ? values.cr_info : '???';
    const cr_url = (values && values.cr_url) ? values.cr_url : '#';

    const ms_href = getIconHref(7);

    if (status !== 'ready' && status !== 'mess') {
        return <Spinner width={widgetWidth} height={widgetHeight} />;
    } else {
        return (
            <div className='widget-container'>
                <div className='widget-content' id='weather'>
                    <div className='week-row option-links'>
                        <div className='left'>
                            <a className="nav-logo big" title={cr_info} href={cr_url}>
                                <svg width="99" height="15" viewBox="0 0 199 30" xmlns="http://www.w3.org/2000/svg">
                                    <title>{cr_info}</title>
                                    <defs>
                                        <linearGradient x1="50%" y1="0%" x2="50%" y2="100%" id="logo-meteosource.inverse-a">
                                            <stop stopColor="#FAD961" offset="0%"></stop>
                                            <stop stopColor="#F76B1C" offset="100%"></stop>
                                        </linearGradient>
                                    </defs>
                                    <g fill="none" fillRule="evenodd">
                                        <path d="M58.813 16.675c.166.317.327.646.48.988.155.341.303.691.444 1.05.142-.367.292-.723.45-1.07.159-.345.321-.68.488-1.006l4.675-9.2c.083-.158.169-.28.256-.368a.84.84 0 01.294-.194c.108-.042.231-.067.369-.075.137-.008.298-.013.481-.013h3.225V25H66.25V14.525c0-.508.025-1.058.075-1.65L61.5 22.238a1.59 1.59 0 01-.606.662c-.254.15-.544.225-.869.225h-.575c-.325 0-.615-.075-.869-.225a1.59 1.59 0 01-.606-.662l-4.85-9.375a15.603 15.603 0 01.1 1.662V25H49.5V6.788h3.225c.183 0 .344.004.481.012.138.008.26.033.369.075a.84.84 0 01.294.194c.087.087.173.21.256.369l4.688 9.237zm19.379-4.838c.858 0 1.643.134 2.356.4a5.122 5.122 0 011.837 1.163 5.306 5.306 0 011.2 1.869c.288.737.432 1.573.432 2.506 0 .292-.013.53-.038.713-.025.183-.07.329-.137.437a.523.523 0 01-.27.225 1.259 1.259 0 01-.43.063h-7.475c.125 1.083.454 1.868.987 2.356.534.487 1.221.731 2.063.731.45 0 .837-.054 1.162-.163.325-.108.615-.229.869-.362.254-.133.487-.254.7-.362.212-.109.435-.163.669-.163.308 0 .541.112.7.337l1.125 1.388a5.76 5.76 0 01-1.294 1.119 6.723 6.723 0 01-1.425.675 7.724 7.724 0 01-1.463.337c-.487.063-.952.094-1.393.094-.909 0-1.76-.148-2.557-.444a5.874 5.874 0 01-2.087-1.319c-.596-.583-1.067-1.308-1.413-2.175-.345-.866-.518-1.874-.518-3.024 0-.867.148-1.688.443-2.463a6.065 6.065 0 011.275-2.037 6.07 6.07 0 012.013-1.388c.787-.342 1.677-.512 2.669-.512zm.075 2.675c-.742 0-1.321.21-1.738.632-.417.42-.691 1.027-.825 1.818h4.838c0-.308-.04-.608-.12-.9a2.182 2.182 0 00-.387-.78 1.972 1.972 0 00-.706-.557c-.292-.142-.646-.213-1.062-.213zM90.458 25.2c-.616 0-1.16-.09-1.63-.269a3.24 3.24 0 01-1.188-.762 3.25 3.25 0 01-.732-1.194 4.621 4.621 0 01-.25-1.563v-6.7h-1.1c-.2 0-.37-.064-.512-.193-.142-.13-.213-.319-.213-.569v-1.512l2.063-.4.762-3.163c.1-.4.384-.6.85-.6h2.025v3.787h3.15v2.65h-3.15v6.438c0 .3.073.548.22.744.145.196.355.294.63.294a1.24 1.24 0 00.607-.144c.07-.038.137-.071.2-.1a.512.512 0 01.218-.044c.117 0 .21.027.282.081.07.054.143.14.218.256l1.175 1.838c-.5.375-1.062.656-1.687.844a6.706 6.706 0 01-1.938.281zm10.667-13.362c.858 0 1.644.133 2.356.4a5.122 5.122 0 011.838 1.162 5.306 5.306 0 011.2 1.869c.287.737.431 1.573.431 2.506 0 .292-.013.53-.038.713-.025.183-.07.329-.137.437a.523.523 0 01-.269.225 1.259 1.259 0 01-.431.063H98.6c.125 1.083.454 1.868.988 2.356.533.487 1.22.731 2.062.731.45 0 .837-.054 1.162-.163.326-.108.615-.229.87-.362.253-.133.487-.254.7-.362.212-.109.435-.163.668-.163.308 0 .542.112.7.337l1.125 1.388a5.76 5.76 0 01-1.294 1.119 6.723 6.723 0 01-1.425.675 7.724 7.724 0 01-1.462.337c-.488.063-.952.094-1.394.094-.908 0-1.76-.148-2.556-.444a5.874 5.874 0 01-2.088-1.319c-.596-.583-1.066-1.308-1.412-2.175-.346-.866-.519-1.874-.519-3.024 0-.867.148-1.688.444-2.463a6.065 6.065 0 011.275-2.037 6.07 6.07 0 012.012-1.388c.788-.342 1.677-.512 2.669-.512zm.075 2.675c-.742 0-1.32.21-1.737.63-.417.422-.692 1.028-.825 1.82h4.837c0-.309-.04-.609-.119-.9a2.182 2.182 0 00-.387-.782 1.972 1.972 0 00-.706-.556c-.292-.142-.646-.213-1.063-.213zm13.417-2.675c.983 0 1.879.154 2.687.462.809.308 1.502.75 2.081 1.325a5.969 5.969 0 011.35 2.094c.321.82.482 1.743.482 2.769 0 1.033-.16 1.964-.482 2.793a6.01 6.01 0 01-1.35 2.113 5.923 5.923 0 01-2.08 1.337c-.81.313-1.705.469-2.688.469-.992 0-1.894-.156-2.707-.469a6.04 6.04 0 01-2.1-1.337 5.923 5.923 0 01-1.362-2.113c-.32-.829-.481-1.76-.481-2.793 0-1.026.16-1.948.48-2.77.322-.82.776-1.518 1.363-2.093a6.01 6.01 0 012.1-1.325c.813-.308 1.715-.463 2.707-.463zm0 10.487c.891 0 1.548-.315 1.968-.944.421-.629.632-1.585.632-2.869 0-1.283-.21-2.237-.632-2.862-.42-.625-1.077-.938-1.968-.938-.917 0-1.588.313-2.013.938-.425.625-.637 1.58-.637 2.862 0 1.284.212 2.24.637 2.87.425.628 1.096.943 2.013.943zm18.541-11.837c-.125.2-.256.35-.393.45a.881.881 0 01-.532.15 1.3 1.3 0 01-.618-.182l-.75-.406a6.224 6.224 0 00-.957-.406 3.826 3.826 0 00-1.225-.181c-.791 0-1.38.168-1.768.506-.388.337-.582.793-.582 1.368 0 .367.117.671.35.913.234.242.54.45.92.625.378.175.812.335 1.3.481.487.146.984.309 1.493.488.508.179 1.006.39 1.494.631.487.242.92.55 1.3.925.379.375.685.831.918 1.369.234.537.35 1.185.35 1.944 0 .841-.145 1.629-.437 2.362a5.532 5.532 0 01-1.269 1.919c-.554.546-1.237.975-2.05 1.287-.812.313-1.735.469-2.769.469a8.875 8.875 0 01-1.73-.175 10.281 10.281 0 01-1.707-.494 9.894 9.894 0 01-1.55-.756 6.586 6.586 0 01-1.263-.975l1.25-1.975a1.098 1.098 0 01.925-.5c.25 0 .502.08.757.238.254.158.541.333.862.524.32.192.69.367 1.106.526.417.158.909.237 1.475.237.767 0 1.363-.169 1.788-.506.425-.338.637-.873.637-1.607 0-.425-.116-.77-.35-1.037a2.704 2.704 0 00-.918-.662c-.38-.176-.81-.33-1.294-.463s-.98-.281-1.488-.444a10.883 10.883 0 01-1.487-.6 4.694 4.694 0 01-1.294-.937 4.387 4.387 0 01-.919-1.45c-.233-.58-.35-1.294-.35-2.144a5.163 5.163 0 011.625-3.738c.534-.508 1.188-.914 1.963-1.218.775-.304 1.662-.456 2.662-.456.559 0 1.102.043 1.632.13.529.088 1.03.217 1.506.388.475.171.919.375 1.331.613.413.237.781.506 1.106.806l-1.05 1.963zm8.842 1.35c.983 0 1.88.154 2.688.462.808.308 1.502.75 2.08 1.325a5.968 5.968 0 011.35 2.094c.322.82.482 1.743.482 2.769 0 1.033-.16 1.964-.481 2.793a6.01 6.01 0 01-1.35 2.113 5.923 5.923 0 01-2.082 1.337c-.808.313-1.704.469-2.687.469-.992 0-1.894-.156-2.706-.469a6.04 6.04 0 01-2.1-1.337 5.923 5.923 0 01-1.363-2.113c-.32-.829-.481-1.76-.481-2.793 0-1.026.16-1.948.481-2.77.321-.82.775-1.518 1.363-2.093a6.01 6.01 0 012.1-1.325c.812-.308 1.714-.463 2.706-.463zm0 10.487c.892 0 1.548-.315 1.969-.944.42-.629.631-1.585.631-2.869 0-1.283-.21-2.237-.631-2.862-.421-.625-1.077-.938-1.969-.938-.917 0-1.587.313-2.012.938-.426.625-.638 1.58-.638 2.862 0 1.284.212 2.24.638 2.87.425.628 1.095.943 2.012.943zm12.017-10.287v8.224c0 .642.145 1.138.437 1.488.292.35.721.525 1.288.525.425 0 .823-.087 1.193-.262.371-.176.732-.421 1.082-.738v-9.237h3.875V25h-2.4c-.484 0-.8-.217-.95-.65l-.238-.75c-.25.242-.508.46-.775.656a4.743 4.743 0 01-.856.5 5.115 5.115 0 01-.981.325c-.35.08-.734.119-1.15.119-.709 0-1.336-.123-1.882-.369a3.87 3.87 0 01-1.38-1.031 4.498 4.498 0 01-.85-1.563 6.462 6.462 0 01-.288-1.974v-8.226h3.875zM164.558 25V12.037h2.3c.192 0 .352.017.482.05.129.034.237.086.325.157.087.07.154.164.2.281.045.117.085.258.118.425l.213 1.213c.475-.734 1.008-1.313 1.6-1.738a3.25 3.25 0 011.937-.638c.592 0 1.067.142 1.425.425l-.5 2.85c-.033.176-.1.298-.2.37a.679.679 0 01-.4.105c-.141 0-.308-.018-.5-.056a3.876 3.876 0 00-.725-.056c-1.016 0-1.816.542-2.4 1.625V25h-3.875zm19.342-9.887c-.117.141-.23.254-.338.337-.108.083-.262.125-.462.125a.996.996 0 01-.519-.137 107.28 107.28 0 00-.518-.307 3.935 3.935 0 00-.675-.306c-.259-.092-.58-.137-.963-.137-.475 0-.885.087-1.231.262a2.28 2.28 0 00-.856.75c-.226.325-.392.723-.5 1.194a7.131 7.131 0 00-.163 1.594c0 1.241.24 2.195.719 2.862.479.667 1.14 1 1.981 1 .45 0 .806-.056 1.069-.169.262-.112.485-.237.669-.375l.506-.381a.936.936 0 01.581-.175c.308 0 .542.112.7.337l1.125 1.388a6.121 6.121 0 01-2.619 1.794 7 7 0 01-1.394.337c-.466.063-.92.094-1.362.094-.792 0-1.548-.15-2.269-.45a5.558 5.558 0 01-1.9-1.306c-.546-.571-.979-1.273-1.3-2.107-.32-.833-.481-1.783-.481-2.85 0-.933.14-1.806.419-2.618a5.945 5.945 0 011.237-2.113 5.754 5.754 0 012.025-1.406c.804-.342 1.736-.512 2.794-.512 1.017 0 1.908.162 2.675.487.767.325 1.458.8 2.075 1.425l-1.025 1.363zm8.017-3.275c.858 0 1.643.133 2.356.4a5.122 5.122 0 011.837 1.162 5.306 5.306 0 011.2 1.869c.288.737.432 1.573.432 2.506 0 .292-.013.53-.038.713-.025.183-.07.329-.137.437a.523.523 0 01-.27.225 1.259 1.259 0 01-.43.063h-7.475c.125 1.083.454 1.868.987 2.356.534.487 1.221.731 2.063.731.45 0 .837-.054 1.162-.163.325-.108.615-.229.869-.362.254-.133.487-.254.7-.362.212-.109.435-.163.669-.163.308 0 .541.112.7.337l1.125 1.388a5.76 5.76 0 01-1.294 1.119 6.723 6.723 0 01-1.425.675 7.724 7.724 0 01-1.463.337c-.487.063-.952.094-1.393.094-.909 0-1.76-.148-2.557-.444a5.874 5.874 0 01-2.087-1.319c-.596-.583-1.067-1.308-1.413-2.175-.345-.866-.518-1.874-.518-3.024 0-.867.148-1.688.443-2.463a6.065 6.065 0 011.275-2.037 6.07 6.07 0 012.013-1.388c.787-.342 1.677-.512 2.669-.512zm.075 2.675c-.742 0-1.321.21-1.738.63-.417.422-.691 1.028-.825 1.82h4.838c0-.309-.04-.609-.12-.9a2.182 2.182 0 00-.387-.782 1.972 1.972 0 00-.706-.556c-.292-.142-.646-.213-1.062-.213z" fill="#FFF"></path>
                                        <path d="M6.948 29h23.62l.37-.035C34.924 28.585 38 25.204 38 21.14c0-4.342-3.496-7.86-7.806-7.86-.661 0-1.31.083-1.938.244l-1.097.282-.144-1.124C26.384 7.742 22.187 4 17.194 4 11.725 4 7.29 8.462 7.29 13.969c0 .529.041 1.052.122 1.567l.164 1.046-1.054.104C3.403 16.994 1 19.646 1 22.828c0 3.275 2.54 5.973 5.768 6.161l.18.011z" stroke="url(#logo-meteosource.inverse-a)" strokeWidth="2"></path>
                                    </g>
                                </svg>
                                <span className="visually-hidden">Weather API</span>
                            </a>

                            <a className="nav-logo small" title={cr_info} href={cr_url}>
                                <img className="weather-icon" src={ms_href} alt="Weather Now icon"/>
                                <span className="visually-hidden">Weather API</span>
                            </a>

                            <button type='button' className={'option-link' + (period === 'now' ?  ' active' : '')} onClick={() => setPeriodOption('now')}  >Сейчас</button>
                            <button type='button' className={'option-link' + (period === 'day' ?  ' active' : '')} onClick={() => setPeriodOption('day')}  >Сутки</button>
                            <button type='button' className={'option-link' + (period === 'week' ? ' active' : '')} onClick={() => setPeriodOption('week')} >Неделя</button>
                        </div>
                        <Form className='right location-form' method="post" onSubmit={handleSubmit}>
                            {brsrLoc ? <></>: <>
                                <input className='location-name' type="text" name="location" defaultValue={location} />
                                <button className='location-btn' type="submit">Go</button>
                                </>
                            }
                            <input className='location-cb' type="checkbox" name="use-browser-location" checked={brsrLoc} onChange={onChangeBrsrLoc} />
                        </Form>
                    </div>
                    {
                        status === 'mess' ? <WeatherMessage     message={message} /> :
                        period === 'now' ?  <WeatherNow         values={values} /> :
                        period === 'day' ?  <WeatherForTheDay   values={values} /> :
                        period === 'week' ? <WeatherForTheWeek  values={values} /> : 
                        <></>
                     }
                    </div>
            </div>
        );
    }
}
