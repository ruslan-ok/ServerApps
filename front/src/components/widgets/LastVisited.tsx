import { useState, useEffect } from 'react';
import Spinner from '../Spinner';
import { apiUrl } from '../auth/Auth';

export default function LastVisited({screenWidth}: {screenWidth: number}) {
    const [status, setStatus] = useState('init');
    const [values, setValues] = useState<any>(null);
    const [message, setMessage] = useState('');

    useEffect(() => {

        async function getData() {
            setStatus('updating');
            const url = apiUrl + `api/get_chart_data/?mark=visited`;
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
                    setValues(resp_data);
                    if (resp_data.result == 'ok') {
                        setStatus('ready');
                    }
                    else {
                        setStatus('mess');
                        setMessage(resp_data.procedure + ': ' + resp_data.info);
                    }
                }
            }
        }

        getData();
    }, []);

    const widgetWidth = screenWidth < 600 ? 410 : (screenWidth < 768 ? 500 : 600);
    const widgetHeight = screenWidth < 600 ? 200 : (screenWidth < 768 ? 250 : 300);

    if (status != 'ready' && status != 'mess') {
        return <Spinner width={widgetWidth} height={widgetHeight} />;
    } else
        if (status == 'mess') {
            return <p>{message}</p>;
        } else {
            var links = values.data.map((page: any) => {
                return (
                    <tr key={ page.id }>
                        <td><i className={ page.icon } title={ page.stamp }></i></td>   
                        <td><a href={ page.url }>{ page.title }</a></td> 
                    </tr>
                );
            });

            return (
                <div className='widget-container'>
                    <div className='widget-content' id='last-visited'> 
                        <h5 className="">{values.title}</h5>
                        <table className="info-table">
                            <tbody>
                                {links}
                            </tbody>
                        </table>
                    </div>
                </div>
            );
        }
}