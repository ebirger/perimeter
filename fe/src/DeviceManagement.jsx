import React, { useEffect, useState } from "react";
import PropTypes from 'prop-types';
import { StopOutlined, CheckOutlined, DeleteOutlined } from '@ant-design/icons';
import { Space, Table, Button, Spin } from 'antd';
import ouiData from "oui-data" with {type: "json"};
import { csrftoken } from './utils.js';

const API_URL = "/api/devices";

const DATE_FORMAT_OPTIONS = {
  year: "numeric",
  month: "long",
  day: "numeric",
  hour: "numeric",
  minute: "numeric",
  second: "numeric",
  timeZoneName: "short"
};

const dateFormat = new Intl.DateTimeFormat('en-US', DATE_FORMAT_OPTIONS);

const getHardwareByMac = (mac) => {
  const oui = mac.replace(/[^0-9a-f]/gi,"").toUpperCase().substring(0,6);
  const vendor = ouiData[oui];
  return vendor?.split('\n')[0];
}

export default function DeviceManagement(props) {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);

  let actions = [];

  const BlockAction = {
    name: 'Block',
    icon: StopOutlined,
    state: 'blocked'
  };
  const AllowAction = {
    name: 'Allow',
    icon: CheckOutlined,
    state: 'allowed'
  };
  const DeleteAction = {
    name: 'Delete',
    icon: DeleteOutlined,
    state: 'deleted'
  };

  switch (props.state) {
  case 'pending':
      actions = [BlockAction, AllowAction, DeleteAction]
      break;
  case 'blocked':
      actions = [AllowAction, DeleteAction]
      break;
  case 'allowed':
      actions = [BlockAction, DeleteAction]
      break;
  };

  const handleAction = async (state, record) => {
    console.log(`handleAction: ${state} ${record.id}`);
    const url = `${API_URL}/${record.id}/`;
    if (state === 'deleted') {
      await fetch(url, {
        credentials: 'include',
        method: 'DELETE',
        mode: 'same-origin',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        }
      });
    } else {
      await fetch(url, {
        credentials: 'include',
        method: 'PATCH',
        mode: 'same-origin',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({'status': state})
      });
    }
    const resp = await fetch(`${API_URL}/`);
    setDevices(await resp.json());
  };

  const dataSource = devices.filter(d=>d['status'] === props.state).map((device, idx) => (
      {
        key: idx + 1,
        id: device.id,
        name: device.hostname,
        mac: device.mac_address,
        hw: getHardwareByMac(device.mac_address),
        ip: device.ip_address,
        last_seen: device.last_seen,
      }
  ));

  const getFilters = (c) => {
      return {
        filterSearch: true,
        onFilter: (value, record) => record[c] && record[c].startsWith(value),
        filters: ([...new Set(dataSource.map(d => d[c]))])
          .sort().filter(v => v).map((v) => ({ text: v, value: v }))
      };
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      ...getFilters('name'),
    },
    {
      title: 'MAC Address',
      dataIndex: 'mac',
      key: 'mac',
      ...getFilters('mac'),
    },
    {
      title: 'Hardware',
      dataIndex: 'hw',
      key: 'hw',
      responsive: ['md'],
      ...getFilters('hw'),
    },
    {
      title: 'IP Address',
      dataIndex: 'ip',
      key: 'ip',
      ...getFilters('ip'),
    },
    {
      title: 'Last Seen',
      dataIndex: 'last_seen',
      key: 'last_seen',
      responsive: ['md'],
      sorter: (a, b) => new Date(a.last_seen) - new Date(b.last_seen),
      render: (_, record) => dateFormat.format(new Date(record.last_seen)),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          {actions.map((a) => <Button
                               key={a.state}
                               icon={React.createElement(a.icon)}
                               onClick={() => handleAction(a.state, record)}
                              >
                                {a.name}
                              </Button>)
          }
        </Space>
      ),
    },
  ];

  useEffect(() => {
    const load = async () => {
      const resp = await fetch(`${API_URL}/`);
      setLoading(false);
      if (!resp.ok) {
        console.error('Failed to fetch devices');
        return;
      }
      setDevices(await resp.json());
    };
    load();
  }, []);

  return (loading ? <Spin /> :
    <Table tableLayout="auto" columns={columns} dataSource={dataSource} />
  );
}

DeviceManagement.propTypes = {
  state: PropTypes.string.isRequired,
};
