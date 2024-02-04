import { useState, useEffect } from "react";

const useFetch = (url) => {
    const [data, setData] = useState(null);
    const [isPending, setIsPending] = useState(true);
    const [error, setError] = useState(null);

    const executeFetch = () => {
        setIsPending(true);

            
        fetch(url, {
            headers: {
            'Content-Type': 'application/json',  // Ensure this header is set
            },
        })
            .then(res => {
                if (!res.ok) {
                    throw Error('Could not fetch data from the resource');
                }
                return res.json();
            })
            .then(data => {
                setData(data);
                setIsPending(false);
                setError(null);
            })
            .catch(err => {
                setIsPending(false);
                setError(err.message);
            });
    };

    useEffect(() => {
        executeFetch();
    }, [url]);

    return { data, isPending, error, executeFetch };
};

export default useFetch;
