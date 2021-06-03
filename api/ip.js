// yarn add axios
import axios from 'axios'

import {NowRequest, NowResponse} from '@now/node'

export default async (req: NowRequest, res: NowResponse) => {
    const ip = req.query.ip || req.headers['x-forwarded-for'] || req.connection.remoteAddress;
    // use https://ip-api.com/
    const respData = await axios.get(
        `https://vercel.x-mx.ml/api/api/?ip=${ip}`
    )
    res.json(respData.data)
}