import './SidebarRight.css';

type Asset = {
    image: string;
    [key: string]: unknown;
};

const not_editable = ["image"]

type SidebarRightProps = {
    selectedAsset:Asset | null;
    setAssets: React.Dispatch<React.SetStateAction<Asset[] | []>>;
    setSelectedAsset: React.Dispatch<React.SetStateAction<Asset | null>>;
}
function SidebarRight({selectedAsset, setAssets, setSelectedAsset} : SidebarRightProps){
    const asset = selectedAsset
    
    return (
    <div className='SideBarRight'>
    {
        asset === null && <p>Wählen Sie ein beliebiges Asset aus, um verfügbare Parameter zu variieren</p>
    }
    

    {asset &&
        Object.entries(asset).map(([name, value]) => (
            <div key={name}>
                <label>{name}: </label>

                <input
                    type={typeof value === 'boolean' ? 'checkbox' : typeof value === 'number' ? 'number' : 'text'}
                    {...(typeof value === 'boolean'
                        ? {checked: value}
                        : {value: String(value)})}
                    disabled={not_editable.includes(name)}
                    onChange={(e) => {
                        const nextValue = typeof value === 'boolean'
                            ? e.currentTarget.checked
                            : typeof value === 'number'
                                ? Number(e.currentTarget.value)
                                : e.currentTarget.value;
                        setAssets(prev => prev.map(object =>
                            object.name === selectedAsset.name
                                ? {...object, [name]: nextValue}
                                : object
                        ));
                        setSelectedAsset(prev => prev && prev.name === selectedAsset.name
                            ? {...prev, [name]: nextValue}
                            : prev
                        );
                    }
                    }
                />
            </div>
        ))
    }
</div>
);
}
export default SidebarRight;